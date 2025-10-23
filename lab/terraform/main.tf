# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Definition of local variables
locals {
  base_apis = [
    "container.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "cloudprofiler.googleapis.com"
  ]
  cluster_name     = google_container_cluster.my_cluster.name
  terraform_path   = path.module
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = var.gcp_project_id
  service = each.key
}

# Enable Google Cloud APIs
module "enable_google_apis" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 18.0"

  project_id                  = var.gcp_project_id
  disable_services_on_destroy = false

  # activate_apis is the set of base_apis and the APIs required by user-configured deployment options
  activate_apis = local.base_apis
}

# Create GKE cluster
resource "google_container_cluster" "my_cluster" {

  name     = var.gcp_cluster_name
  location = var.gcp_zone
  project  = var.gcp_project_id 
  network  = var.gcp_network

  # Set an empty ip_allocation_policy to allow autopilot cluster to spin up correctly
  ip_allocation_policy {
  }

  # Avoid setting deletion_protection to false
  # until you're ready (and certain you want) to destroy the cluster.
  # deletion_protection = false

  depends_on = [
    module.enable_google_apis
  ]

  # Removes the implicit default node pool, recommended when using
  # google_container_node_pool.
  remove_default_node_pool = true
  initial_node_count       = 1
}

# Service Account for nodes
resource "google_service_account" "gke_sa" {
  account_id   = "gke-sa"
  display_name = "GKE Service Account"
}

# Small Linux node pool to run some Linux-only Kubernetes Pods.
resource "google_container_node_pool" "linux_pool" {
  name       = "linux-pool"
  project    = google_container_cluster.my_cluster.project
  cluster    = google_container_cluster.my_cluster.name
  location   = google_container_cluster.my_cluster.location
  node_count = 1

  node_config {
    image_type = "COS_CONTAINERD"
    machine_type = "e2-standard-4"
    service_account = google_service_account.gke_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    tags = ["gke-node"]
  }
}

# Node pool of ARM-based Linux machines.
resource "google_container_node_pool" "arm_pool" {
  name       = "arm-pool"
  project    = google_container_cluster.my_cluster.project
  cluster    = google_container_cluster.my_cluster.name
  location   = google_container_cluster.my_cluster.location
  node_count = 1
  node_config {
    image_type = "COS_CONTAINERD"
    machine_type = "c4a-standard-16"
    service_account = google_service_account.gke_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    tags = ["gke-node"]
  }
}

# Get credentials for cluster and apply kustomize manifests
resource "null_resource" "kubectl_config" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command = <<EOT
rm -rf /root/google-cloud-sdk;
curl https://sdk.cloud.google.com > install.sh;
bash install.sh --disable-prompts;
source /root/google-cloud-sdk/path.bash.inc;
gcloud components install kubectl beta --quiet;
gcloud auth activate-service-account --key-file ${var.service_account_key_file};
gcloud container clusters get-credentials ${local.cluster_name} --zone=${var.gcp_zone} --project=${var.gcp_project_id};
kubectl apply -k ${local.terraform_path}/${var.filepath_manifest} -n ${var.namespace}
EOT
  }
  depends_on = [
    google_container_node_pool.arm_pool,
    google_container_node_pool.linux_pool
  ]
}