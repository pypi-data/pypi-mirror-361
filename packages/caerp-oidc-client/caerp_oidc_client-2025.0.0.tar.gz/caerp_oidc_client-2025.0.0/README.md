# Pyramid Oidc client library for caerp


```python
python setup.py install
```

## Add a client in your OpenId Authentication (e.g: Keycloak)


To configure your open id connect client in a SSO server like Keycloak.

Host : https://caerp.mycae.coop

> **Important** Create a custom realm (don't use the master realm, you'll face serious security problems : all users would have admin rights on Keycloak)

### Add a client

- ClientID : caerp_client_id
- Name : Free choice
- Root URL : https://caerp.mycae.coop
- Home URL : https://caerp.mycae.coop
- Valid Redirect URIs : https://caerp.mycae.coop/*
- Valid post logout redirect URIs : https://caerp.mycae.coop/login
- Web Origins : https://caerp.mycae.coop
- Admin URL : Nothing
- Client Authentication : True
- Authentication Flow : Check the following
   - Standard Flow
   - Implicit flow
   - Direct access grants
- Disable Consent required
- Backchannel logout url : https://caerp.mycae.coop/oidc_backend_logout
- Backchannel logout session required: True   

### Retrieve the client secret


In the "Credentials" section of the keycloak client view, retrieve the client's secret (you need it to configure caerp)


## Configure your client : caerp

In your caerp application's ini file

```
pyramid.includes = ...
                   caerp_oidc_client.models
```

Later in the same ini file 
```
caerp.authentification_module=caerp_oidc_client

oidc.client_secret=<Secret token from the OIDC server>
oidc.client_id=caerp_client_id
oidc.scope=openid roles
oidc.auth_endpoint_url=<Keycloak auth endpoint url>
oidc.token_endpoint_url=<Keycloak id token endpoint url>
oidc.logout_endpoint_url=<Keycloak logout endpoint url>
```

Keycloak's url are in the form 

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/auth

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/token

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/logout 