exit_after_auth = false
pid_file = "/home/vault/pidfile"
auto_auth {
    method "kubernetes" {
        mount_path = "auth/kubernetes"
        config = {
            role = "stackl"
        }
    }
    sink "file" {
        config = {
            path = "/home/vault/.vault-token"
        }
    }
}

template {
//  contents = <<EOH
//  {{- with secret (env "SECRET_PATH") }}{{ .Data.data | toJSON }}{{ end }}
//  EOH
  source = "/etc/vault-agent/template.ctmpl"
  destination = "/etc/vault-agent/credentials.json"
}