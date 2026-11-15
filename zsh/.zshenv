# Remote deployments need the same 1Password identity in interactive terminals
# and noninteractive zsh commands. Keep the token machine-local and preserve
# an explicitly supplied identity. Ordinary local shells use desktop sign-in.
if [[ ( -n "${SSH_CONNECTION:-}" || -n "${HERDR_ENV:-}" ) &&
      -z "${OP_SERVICE_ACCOUNT_TOKEN:-}" &&
      -r "$HOME/.config/op/homelab-service-account-token" ]]; then
  export OP_SERVICE_ACCOUNT_TOKEN="$(< "$HOME/.config/op/homelab-service-account-token")"
fi
