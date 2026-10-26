---
title: Zimbra cert replace
description: Howto replace cert in zimbra
published: true
date: 2026-10-26T14:12:12.616Z
tags: zimbra, certificate
editor: markdown
dateCreated: 2026-02-15T07:44:06.633Z
---

# Zimbra SSL Cert Replace

## Links
* https://www.ssls.com/knowledgebase/how-to-install-an-ssl-certificate-on-zimbra/
* https://www.digicert.com/kb/csr-creation-ssl-installation-zimbra.htm
* https://www.digicert.com/kb/ssl-support/pem-ssl-creation.htm
* https://www.bitbull.ch/wiki/index.php/Openssl_Notes

## Download Certificate (just valid for acme)
* https://www.thesslstore.com/
* My Orders > Total Orders > "latest order with active status" > Download Certificate
* Server Platform: nginx / File Type: Individual .crts (zipped) -> star_acme.com.pem file

## Backup current certificates
```
root@acme-mail-01:~# backup /opt/zimbra/ssl/zimbra/commercial
'/opt/zimbra/ssl/zimbra/commercial' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657'
'/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial_ca.crt'
'/opt/zimbra/ssl/zimbra/commercial/commercial.crt' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.crt'
'/opt/zimbra/ssl/zimbra/commercial/commercial.key' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.key'
'/opt/zimbra/ssl/zimbra/commercial/commercial.csr' -> '/opt/zimbra/ssl/zimbra/commercial.202306110657/commercial.csr'
```

## Verify current Certificate
```
zimbra@acme-mail-01:~$ /opt/zimbra/bin/zmcertmgr verifycrt comm                                                  
** Verifying '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' against '/opt/zimbra/ssl/zimbra/commercial/commercial.key'
Certificate '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' and private key '/opt/zimbra/ssl/zimbra/commercial/commercial.key' match.
** Verifying '/opt/zimbra/ssl/zimbra/commercial/commercial.crt' against '/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt'
Valid certificate chain: /opt/zimbra/ssl/zimbra/commercial/commercial.crt: OK

zimbra@acme-mail-01:/tmp$ openssl verify -CAfile /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt /opt/zimbra/ssl/zimbra/commercial/commercial.crt
/opt/zimbra/ssl/zimbra/commercial/commercial.crt: OK

zimbra@acme-mail-01:/tmp$ cd /tmp
zimbra@acme-mail-01:/tmp$ wget https://raw.githubusercontent.com/joe-speedboat/linux.scripts/master/shell/openssl_check_cert_chain.sh

zimbra@acme-mail-01:/tmp$ bash openssl_check_cert_chain.sh /opt/zimbra/ssl/zimbra/commercial/commercial.crt 
 0: subject=C = US, ST = Nevada, L = StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
 1: subject=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
 2: subject=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
/opt/zimbra/ssl/zimbra/commercial/commercial.crt: OK

zimbra@acme-mail-01:/tmp$  openssl x509 -in /opt/zimbra/ssl/zimbra/commercial/commercial.crt -text -noout | head
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            77:66:55:44:33:22:11:77:66:55:44:33:22:11:11:11
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
        Validity
            Not Before: YYY
            Not After: ZZZ
```

## Prepare new Certificate
Create/Edit this tree files:
```
/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt
# ca chain without server certificate

/opt/zimbra/ssl/zimbra/commercial/commercial.crt
# server certificate (note that old certs above had ca included, which is wrong but no show stopper)

/opt/zimbra/ssl/zimbra/commercial/commercial.key
# private key
```

## Verify new Certificate
```
root@acme-mail-01:~# bash /tmp/openssl_check_cert_chain.sh /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt 
 0: subject=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
 1: subject=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
/opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt: OK

root@acme-mail-01:~#  cat /opt/zimbra/ssl/zimbra/commercial/commercial.crt /opt/zimbra/ssl/zimbra/commercial/commercial_ca.crt > /tmp/tmp.crt
root@acme-mail-01:~# bash /tmp/openssl_check_cert_chain.sh /tmp/tmp.crt 
 0: subject=C = US, ST = Nevada, L = StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
 1: subject=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
 2: subject=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
issuer=C = US, O = DigiCert Inc, OU = www.digicert.com, CN = DigiCert Global Root G2
/tmp/tmp.crt: OK

root@acme-mail-01:~# openssl x509 -in /opt/zimbra/ssl/zimbra/commercial/commercial.crt -text -noout | head
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
        Validity
            Not Before: YYY
            Not After: ZZZ

root@acme-mail-01:~# su - zimbra
zimbra@acme-mail-01:~$ cd /opt/zimbra/ssl/zimbra/commercial/
zimbra@acme-mail-01:~/ssl/zimbra/commercial$ zmcertmgr verifycrt comm commercial.key commercial.crt commercial_ca.crt
** Verifying 'commercial.crt' against 'commercial.key'
Certificate 'commercial.crt' and private key 'commercial.key' match.
** Verifying 'commercial.crt' against 'commercial_ca.crt'
Valid certificate chain: commercial.crt: OK
```

## Deploy new Certificates
```
root@acme-mail-01:~# su - zimbra
zimbra@acme-mail-01:~$ cd /opt/zimbra/ssl/zimbra/commercial/
zimbra@acme-mail-01:~/ssl/zimbra/commercial$ zmcertmgr verifycrt comm commercial.key commercial.crt commercial_ca.crt
** Verifying 'commercial.crt' against 'commercial.key'
Certificate 'commercial.crt' and private key 'commercial.key' match.
** Verifying 'commercial.crt' against 'commercial_ca.crt'
Valid certificate chain: commercial.crt: OK

zimbra@acme-mail-01:~/ssl/zimbra/commercial$ zmcertmgr deploycrt comm commercial.crt commercial_ca.crt
[...]
# watch out for any errors

zimbra@acme-mail-01:~/ssl/zimbra/commercial$ zmcertmgr viewdeployedcrt
- imapd: /opt/zimbra/conf/imapd.crt
notBefore=xxx
notAfter=xxx
subject=C = US, ST = Nevada, L = StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
SubjectAltName=*.acme.com
- ldap: /opt/zimbra/conf/slapd.crt
notBefore=xxx
notAfter=xxx
subject=C = US, ST = Nevada, L = StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
SubjectAltName=*.acme.com
- mailboxd: /opt/zimbra/mailboxd/etc/mailboxd.pem
notBefore=xxx
notAfter=xxx
subject=C = US, ST = Nevada, L =StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
SubjectAltName=*.acme.com
- mta: /opt/zimbra/conf/smtpd.crt
notBefore=xxx
notAfter=xxx
subject=C = US, ST = Nevada, L =StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
SubjectAltName=*.acme.com
- proxy: /opt/zimbra/conf/nginx.crt
notBefore=xxx
notAfter=xxx
subject=C = US, ST = Nevada, L =StoneBridge, O = Coyote Enterprises, CN = *.acme.com
issuer=C = US, O = DigiCert Inc, CN = DigiCert Global G2 TLS RSA SHA256 2020 CA1
SubjectAltName=*.acme.com

zimbra@acme-mail-01:~/ssl/zimbra/commercial$ zmcontrol restart
Host mail01.acme.com
        Stopping vmware-ha...Done.
        Stopping zmconfigd...Done.
        Stopping zimlet webapp...Done.
        Stopping zimbraAdmin webapp...Done.
        Stopping zimbra webapp...Done.
        Stopping service webapp...Done.
        Stopping stats...Done.
        Stopping mta...Done.
        Stopping spell...Done.
        Stopping snmp...Done.
        Stopping cbpolicyd...Done.
        Stopping archiving...Done.
        Stopping opendkim...Done.
        Stopping amavis...Done.
        Stopping antivirus...Done.           
        Stopping antispam...Done.
        Stopping proxy...Done.
        Stopping memcached...Done.
        Stopping mailbox...Done.
        Stopping convertd...Done.
        Stopping logger...Done.
        Stopping dnscache...Done.
        Stopping ldap...Done.
Host mail01.acme.com
        Starting ldap...Done.
        Starting zmconfigd...Done.
        Starting logger...Done.
        Starting convertd...Done.
        Starting mailbox...Done.
        Starting memcached...Done.
        Starting proxy...Done.
        Starting amavis...Done.
        Starting antispam...Done.
        Starting antivirus...Done.
        Starting snmp...Done.
        Starting spell...Done.
        Starting mta...Done.
        Starting stats...Done.
        Starting service webapp...Done.
        Starting zimbra webapp...Done.
        Starting zimbraAdmin webapp...Done.
        Starting zimlet webapp...Done.
```
