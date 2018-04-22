#!/bin/bash

# ---------------------------------------------------------
# CUSTOMIZATION:

CSR_SUBJECT_C="EE"
CSR_SUBJECT_ST="Estonia"
CSR_SUBJECT_L="Tallinn"

# ---------------------------------------------------------
# VALIDATE CONSOLE ARGS
#
# PROG=$(basename "$0")
HERE=$(cd "$(dirname "$0")" && pwd)
# DOMAIN="${1}"

# if [ -z "$DOMAIN" ]; then
#     echo "Usage: ${PROG} <domain>"
#     exit 1
# fi
# ---------------------------------------------------------


function generate_subject () {
    declare -r target_domain="${1}"
    shift
    cat <<EOF
C=${CSR_SUBJECT_C}
ST=${CSR_SUBJECT_ST}
L=${CSR_SUBJECT_L}
O=${target_domain#*.}
CN=${target_domain}
OU=${target_domain#*.}
emailAddress=infosec@${target_domain#*.}
subjectAltName=DNS:${target_domain}
EOF
    echo
}

file_prefix="lets_encrypt"
private_key_filename="${file_prefix}.account.key"
public_key_filename="${private_key_filename}.pub"


declare -a DOMAINS


# DOMAINS+=( aes.python.clinic )
DOMAINS+=( api.python.clinic )
# DOMAINS+=( audio.python.clinic )
DOMAINS+=( blog.python.clinic )
# DOMAINS+=( box.python.clinic )
# DOMAINS+=( cdn.python.clinic )
# DOMAINS+=( chat.python.clinic )
# DOMAINS+=( cipher.python.clinic )
# DOMAINS+=( ciphertext.python.clinic )
# DOMAINS+=( cloud.python.clinic )
# DOMAINS+=( crypt0.python.clinic )
# DOMAINS+=( crypto.python.clinic )
# DOMAINS+=( data.python.clinic )
# DOMAINS+=( dist.python.clinic )
# DOMAINS+=( downloads.python.clinic )
# DOMAINS+=( drive.python.clinic )
# DOMAINS+=( drop.python.clinic )
# DOMAINS+=( dropbox.python.clinic )
# DOMAINS+=( email.python.clinic )
# DOMAINS+=( files.python.clinic )
# DOMAINS+=( github.python.clinic )
# DOMAINS+=( gnu.python.clinic )
# DOMAINS+=( gpg.python.clinic )
# DOMAINS+=( h4x0r.python.clinic )
# DOMAINS+=( info.python.clinic )
DOMAINS+=( io.python.clinic )
# DOMAINS+=( jabber.python.clinic )
DOMAINS+=( mail.python.clinic )
# DOMAINS+=( media.python.clinic )
# DOMAINS+=( onion.python.clinic )
# DOMAINS+=( opensource.python.clinic )
# DOMAINS+=( pgp.python.clinic )
# DOMAINS+=( pop.python.clinic )
DOMAINS+=( private.python.clinic )
# DOMAINS+=( projects.python.clinic )
# DOMAINS+=( public.python.clinic )
# DOMAINS+=( secure.python.clinic )
# DOMAINS+=( smtp.python.clinic )
# DOMAINS+=( static.python.clinic )
# DOMAINS+=( tor.python.clinic )
# DOMAINS+=( video.python.clinic )
# DOMAINS+=( voip.python.clinic )
# DOMAINS+=( web.python.clinic )
# DOMAINS+=( webrtc.python.clinic )
# DOMAINS+=( www.python.clinic )

DOMAINS+=( xmpp.python.clinic )

echo -e "\033[1;30mDOMAINS:\n${DOMAINS[*]}\033[0m" | tr '[:space:]' '\n'

function handle_error() {
    echo -ne "\033[0m"
    reason="${1}"
    shift
    echo -ne "\033[1;37mError: \033[0;31m${reason}\033[0m\n"
    echo -ne "\033[1;37musing password: \033[0;31m${reason}\033[0m\n"
    exit 1
}

function handle_success() {
    echo -ne "\033[0m"
    reason="${1}"
    shift
    echo -ne "\033[1;37mSuccess: \033[0;32m${reason}\033[0m\n"
}

function handle_info() {
    echo -ne "\033[0m"
    reason="${1}"
    shift
    echo -ne "\033[1;37mInfo: \033[0;34m${reason}\033[0m\n"
}

function handle_metadata() {
    echo -ne "\033[0m"
    reason="${1}"
    shift
    echo -ne "\033[0;33m${reason}\033[0m\n"
}


# generate private keys
if [ ! -f "${private_key_filename}" ]; then
    if openssl genrsa 4096 > "${private_key_filename}"; then
        cp -v $private_key_filename user.key
        handle_success "generated key: ${private_key_filename}"
    else
        handle_error "failed to generate private key: ${private_key_filename}"
    fi
fi


if [ ! -f "${public_key_filename}" ]; then
    # derive public key
    if openssl rsa -in "${private_key_filename}" -pubout > "${public_key_filename}"; then
        handle_success "derived public key: ${public_key_filename} from ${private_key_filename}"
    else
        handle_error "failed to derive public key: ${public_key_filename} from ${private_key_filename}"
    fi
fi

for current in ${DOMAINS[*]}; do
    domain_private_key_filename="${file_prefix}.${current}.key"

    csr_filename="${file_prefix}.${current}.csr"
    cert_filename="${file_prefix}.${current}.cert"

    if [ ! -f "${domain_private_key_filename}" ]; then
        if openssl genrsa 4096 > "${domain_private_key_filename}"; then
            handle_success "generated key: ${domain_private_key_filename}"
        else
            handle_error "failed to generate private key: ${domain_private_key_filename}"
        fi
    fi

    EMAIL="infosec@${current#*.}"
    CSRSBJCT="$(generate_subject "${current}" | tr "\n" "/")"
    echo -e "\033[1;30mCSR Subject:\n${CSRSBJCT}\033[0m" | tr '[:space:]' '\n'

    if [ ! -f "${csr_filename}" ]; then
        # Generate the CSR
        if openssl req \
                   -new \
                   -batch \
                   -subj "/${CSRSBJCT%%/}" \
                   -key "${domain_private_key_filename}" \
                   -out "${csr_filename}" ; then
            handle_success "generated self-signed certificate request: ${csr_filename} with key ${domain_private_key_filename}"
        else
            handle_error "failed to generate self-signed certificate request: ${csr_filename} with key ${domain_private_key_filename}"
        fi
    fi
    # Generate the cert with letsencrypt
    if [ ! -f "${cert_filename}" ]; then
        if python "${HERE}/sign_csr.py" --email="${EMAIL}" --public-key "${public_key_filename}" "${csr_filename}" > "${cert_filename}"; then
            handle_success "Generated Let's Encrypt Certificate"
        else
            handle_error "Failed to sign CSR with Let's Encrypt"
        fi
    fi
done
