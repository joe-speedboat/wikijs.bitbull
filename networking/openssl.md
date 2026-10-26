---
title: openssl helpers
description: Useful OpenSSL commands
published: true
date: 2026-10-26T14:12:48.588Z
tags: helpers, openssl
editor: markdown
dateCreated: 2026-02-21T20:39:22.190Z
---

## Display/Check

* Display complete certificate
  ```bash
  openssl x509 -noout -text -in <certificate_name.crt>
  ```

* Display the issuer of the certificate
  ```bash
  openssl x509 -noout -issuer -in <certificate_name.crt>
  ```

* For whom was the certificate issued?  
  ```bash
  openssl x509 -noout -subject -in <certificate_name.crt>
  ```

* For which period is the certificate valid?  
  ```bash
  openssl x509 -noout -dates -in <certificate_name.crt>
  echo QUIT | openssl s_client -connect host:443 2>/dev/null | sed -ne '/BEGIN CERT/,/END CERT/p' | openssl x509 -noout -text | grep -A2 Validity
  ```
* Display the above combined
  ```bash
  openssl x509 -noout -issuer -subject -dates -in <certificate_name.crt>
  ```
  
* Display the hash
  ```bash
  openssl x509 -noout -hash -in <certificate_name.crt>
  ```
* Display the MD5 fingerprint
  ```bash
  openssl x509 -noout -fingerprint -in <certificate_name.crt>
  ```
  
* Verify an SSL certificate
  ```bash
  openssl verify -CApath /etc/pki/tls/certs -verbose <certificate_name.crt>
  ```
* Query an SSL port for certificates
  ```bash
  openssl s_client -CApath /etc/pki/tls/certs -connect localhost:636 -showcerts 
  openssl s_client -connect host:443
  printf '' | timeout 20 openssl s_client -starttls smtp -connect "host:25"
  ```
* Extract server key from pfx (PKCS#12)
  ```bash
  openssl pkcs12 -in certname.pfx -nocerts -out key.pem -nodes # extract key
  openssl pkcs12 -in certname.pfx -nokeys -out cert.pem        # export cert 
  openssl rsa -in key.pem -out server.key                      # remove passphrase
  ```

## Retrieve Cert Infos

* Get cert chain from a web service  
  ```bash
  echo | openssl s_client -showcerts -connect www.google.ch:443`
  ```
* To correctly create the cert chain, note the following  
  * The cert chain is assembled in a single UTF-8 file  
    no Windows characters, use Notepad++ with UTF-8 and copy directly from PuTTY  
  * The chain must be ordered as follows (openssl standard, required by VMware products)  
    1. Server cert  
    2. One or more intermediate certs  
    3. Root CA cert  
  * Here is an example  

```
-----BEGIN CERTIFICATE-----
MIIDfTCCAuagAwIBAgIDErvmMA0GCSqGSIb3DQEBBQUAME4xCzAJBgNVBAYTAlVT
... SERVER CERT ...
b8ravHNjkOR/ez4iyz0H7V84dJzjA1BOoa+Y7mHyhD8S
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDfTCCAuagAwIBAgIDErvmMA0GCSqGSIb3DQEBBQUAME4xCzAJBgNVBAYTAlVT
... INTERMEDIATE CERT ...
b8ravHNjkOR/ez4iyz0H7V84dJzjA1BOoa+Y7mHyhD8S
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDfTCCAuagAwIBAgIDErvmMA0GCSqGSIb3DQEBBQUAME4xCzAJBgNVBAYTAlVT
... ROOT CA CERT ...
b8ravHNjkOR/ez4iyz0H7V84dJzjA1BOoa+Y7mHyhD8S
-----END CERTIFICATE-----
```


## Remove/Change Passphrase
* Remove passphrase from a key file
  ```bash
  openssl rsa -in <certificate_name.key> -out <newkeyfile.key>
  ```
* Change passphrase for a key file
  ```bash
  openssl rsa -des3 -in <certificate_name.key> -out <newkeyfile.key>
  ```

## Generate/Display CSR

* Generate a CSR + key file (for requesting a real certificate). The `<certificate_name.csr>` is then sent to the certifying authority, e.g. Thawte etc.  
  * Generate 2048 bit RSA key
    ```bash
    openssl genrsa -out <certificate_name.key> 2048
    ```
  * Generate the CSR
    ```bash
    openssl req -new -key <certificate_name.key> -out <certificate_name.csr>
    ```
  * Protect the key with a passphrase  
    ```bash
    openssl rsa -des3 -in <certificate_name.key> -out <certificate_name.key.sec>
    ```
* Display a CSR (certificate request)  
  ```bash
  openssl req -noout -text -in <request.csr>`
  ```

### Generate CSR for Forman/Satellite
```bash
mkdir /root/certificate
chmod 700 /root/certificate
cd /root/certificate

CSR_C=CH
CSR_ST=St_Gall
CSR_L=Flawil
CSR_O=BITBULL
CSR_OU=IT
CSR_FQDN=$(hostname -f)

echo "
[req]
req_extensions = v3_req
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = $CSR_C
ST = $CSR_ST
L = $CSR_L
O = $CSR_O
OU = $CSR_OU
CN = $CSR_FQDN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth, clientAuth, codeSigning, emailProtection
subjectAltName = @alt_names

[alt_names]
DNS.1 = $CSR_FQDN
" > $CSR_FQDN.cnf

# generate csr and encrypted private key
openssl req -new -out $CSR_FQDN.csr -keyout ${CSR_FQDN}_key.pem -config $CSR_FQDN.cnf

# generate csr and plain private key
openssl req -new -nodes -out $CSR_FQDN.csr -keyout ${CSR_FQDN}_key.pem -config $CSR_FQDN.cnf

# verify csr
openssl req -text -noout -verify -in $CSR_FQDN.csr
```

## Convert Certificates

* PEM to DER  
  ```bash
  openssl x509 -outform der -in certificate.pem -out certificate.der
  ```
* PEM to P7B  
  ```bash
  openssl crl2pkcs7 -nocrl -certfile certificate.cer -out certificate.p7b -certfile CACert.cer
  ```
* PEM to PFX  
  ```bash
  openssl pkcs12 -export -out certificate.pfx -inkey privateKey.key -in certificate.crt -certfile CACert.crt
  ```
* DER to PEM  
  ```bash
  openssl x509 -inform der -in certificate.cer -out certificate.pem
  ```
* P7B to PEM  
  ```bash
  openssl pkcs7 -print_certs -in certificate.p7b -out certificate.cer
  ```
* P7B to PFX  
  ```bash
  openssl pkcs7 -print_certs -in certificate.p7b -out certificate.cer
  openssl pkcs12 -export -in certificate.cer -inkey privateKey.key -out certificate.pfx -certfile CACert.cer
  ```

* PFX to PEM  
  ```bash
  openssl pkcs12 -in certificate.pfx -out certificate.cer -nodes
  ```