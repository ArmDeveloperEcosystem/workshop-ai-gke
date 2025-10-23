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

output "cluster_location" {
  description = "Location of the cluster"
  value       = resource.google_container_cluster.my_cluster.location
}

output "cluster_name" {
  description = "Name of the cluster"
  value       = resource.google_container_cluster.my_cluster.name
}

output "artifact_repo" {
  description = "Name of the artifact repository"
  value       = resource.google_artifact_registry_repository.artifact_registry_creation.name
}

output "vm_instance_name" {
  description = "Name of the VM instance"
  value       = resource.google_compute_instance.arm_vm.name
}

output "vm_instance_zone" {
  description = "Zone of the VM instance"
  value       = resource.google_compute_instance.arm_vm.zone
}