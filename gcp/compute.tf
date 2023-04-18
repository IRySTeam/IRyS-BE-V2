resource "google_compute_instance" "default" {
  name         = "irys-vm"
  machine_type = "e2-standard-2"
  zone         = "asia-southeast2-a"
  tags         = ["ssh"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-minimal-2210-amd64"
    }
  }

  # Change as required
  metadata_startup_script = "sudo apt-get update; sudo apt-get install -yq build-essential python3-pip rsync;"

  network_interface {
    subnetwork = google_compute_subnetwork.default.id

    access_config {
      # Adds Ephemeral External IP
    }
  }
}