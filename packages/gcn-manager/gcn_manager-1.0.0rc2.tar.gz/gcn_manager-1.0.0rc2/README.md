# Manager (in Python) for Gpio Change Notifier clients

# specification

- ENV
    - recipients
        - email -> DONE
        - sms -> DONE
        - twitter -> DONE

- MQTT
    - tls
        - mandatory -> DONE
        - mandatory verification -> DONE
    - auth
        - login/password -> DONE
    - errors
        - retryable
            - dns resolution -> DONE
            - host unreachable -> DONE
            - port unreachable -> DONE
        - fatal
            - auth failed -> DONE
            - tls failed -> DONE

- notifications
    - manager
        - starting -> DONE
        - exiting -> DONE
    - mqtt connection
        - failing -> DONE
        - established -> DONE
    - client
        - status
            - offline -> DONE
            - online -> DONE
        - heartbeat
            - skewed -> DONE
            - missed -> DONE
        - dropped item -> DONE
    - gpio
        - raising -> DONE
        - falling -> DONE

- brain
    - monitored gpio -> DONE
    - gpio initial -> DONE
    - gpio changed -> DONE
    - untracked -> DONE

# TODO

- see TODO/FIXME in project files

- delete non-monitored pins from memory (optional) and mqtt (need acl change)

- implement a safeguard regarding notifications : max N/day

- send a notification for when one of the providers has no low/no resources

- external monitor for the manager, to ensure it is running

- monitor
    - self sms sent and success
    - metrics from gcn client

- dev
    - add tracing
    - add metrics

- mqtt
    - auth client cert (mtls)
    - auth tls preshared key ?
    - using proxy ?

- callback URL
    - id : numéro d'identification du SMS
    - ptt : code qui correspond à un état du SMS. Les différents codes ptt sont décrits dans le premier tableau
      ci-dessous.
    - date : date du DLR (Delivery report)
    - description : ID du DLR . Les différents ID sont décrits dans le second tableau ci-dessous
    - descriptionDlr : description du status du DLR

# python asyncio debug

    export PYTHONASYNCIODEBUG=1

# credentials

## twitter

developer portal https://developer.x.com/en

project / app / keys and token

- Consumer Keys / API Key and Secret : `regenerate`
- Authentication Tokens
    - Bearer Token : **not needed**
    - Access Token and Secret : `regenerate`
- OAuth 2.0 Client ID and Client Secret : `regenerate`

project / app / settings

- oauth 1.0 : `Read and write and Direct message`
- type of app : `native app`
- oauth 2.0 / callback uri : `https://localhost` + mandatory website

_**IMPORTANT**: regenerate `Access Token and Secret` each time you modify oauth 1.0 permissions !_
