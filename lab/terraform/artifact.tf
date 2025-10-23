/********************************************************
Artifact registry for custom container images
********************************************************/

resource "google_artifact_registry_repository" "artifact_registry_creation" {
    location          = var.gcp_region  
    repository_id     = var.gcp_artifact_name
    description       = "Artifact repository"
    format            = "DOCKER"
    depends_on = [
        google_project_service.gcp_services,
    ]  
}