
    resource "google_compute_instance" "arm_vm" {
    name         = "workshop-build-server"
    machine_type = "c4a-highmem-8"
    zone         = var.gcp_zone
    
    boot_disk {
        initialize_params {
            image  = "ubuntu-os-cloud/ubuntu-2204-lts-arm64"
            size   = 200
        }
    }

    network_interface {
        network    = var.gcp_network
        access_config {} # Enables external IP
    }
    metadata = {
    startup-script = <<SCRIPT
        #!/bin/bash
        # Install kubectl
        # curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl"
        # sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        
        # Update Google CLI, kubectl, and gke-auth-plugin
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
        sudo apt-get update && sudo apt-get install google-cloud-cli
        sudo apt-get install -y kubectl
        sudo apt-get install -y google-cloud-sdk-gke-gcloud-auth-plugin
      SCRIPT
    }

    service_account {
        scopes = ["cloud-platform"]
    }
}