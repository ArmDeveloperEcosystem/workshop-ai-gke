
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
}