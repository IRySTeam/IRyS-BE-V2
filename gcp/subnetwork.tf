resource "google_compute_subnetwork" "default" {
  name                     = "private-range"
  ip_cidr_range            = "10.0.0.0/18"
  region                   = "asia-southeast2"
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}