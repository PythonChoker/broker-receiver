# ABOUT THIS REPO
This microservice is used as an entry point for further message distribution (see [Project Summary](#project-summary)).

HTTP functionality is implemented with [Flask](https://flask.palletsprojects.com/).

# DEPENDENCIES
- [Flask](https://flask.palletsprojects.com/)
- [RabbitMQ](https://www.rabbitmq.com/)

# SETUP
- Install the dependencies listed in ```requirements.txt```
- Make copy of the ```config.example.ini``` and name it ```config.ini```
- Fill the RabbitMQ connection requisites in the ```RABBIT``` section of the ```config.ini``` file
- Run the ```deploy.sh``` script to generate the app security token 
- Set Flask app options in the ```APP``` section of the ```config.ini``` file as necessary (see [Config Options](#config-options))

# CONFIG OPTIONS
| Option               | Type   | Description                                                                   |
|----------------------|--------|-------------------------------------------------------------------------------|
| app_key              | string | Security token used for incoming requests. Generated with the ```deploy.sh``` |
| debug                | bool   | Run the Flask app in debug mode                                               |
| host                 | string | Host of the Flask app                                                         |
| port                 | int    | Port of the Flask app                                                         |
| max_text_len         | int    | Maximum message length in characters                                          |
| max_attachment_size  | int    | Maximum attached files size in MB                                             |
| queue_dispatcher     | string | Name of the RabbitMQ queue handling the encoded message dispatching           |

# SENDING REQUESTS
The microservice accepts POST requests with multipart/form-data content type.

A request shall include a bearer token containing the security token specified in the ```app_key``` option of the ```config.ini``` file (see [Config Options](#config-options)).

## Request Parameters
| Parameter    | Type            | Required                 | Description                                                                                                                  |
|--------------|-----------------|--------------------------|------------------------------------------------------------------------------------------------------------------------------|
| project_id   | int             | yes                      | Id of the project. Must be greater than 0                                                                                    |
| text         | string          | yes if no files attached | Text of the message. Must not be longer than the ```max_text_len``` option in the ```config.ini``` file                      |
| attachments  | array of files  | yes if the text is empty | Files to attach to the message. Total size must not exceed the ```max_attachment_size``` option in the ```config.ini``` file |

## Supported File MIME Types
Each endpoint microservice supports its own MIME types for attachments depending on the system. E.g., SMTP BZ can attach
any kind of file to an e-mail, but Telegram has its own limitations. As result, every endpoint may or may not attach
certain files to a message.

Hence, in order to ensure that each endpoint would send message with all files attached, it is recommended to limit the
attachments to the following MIME types:

| Type    | Max Size | MIME                     |
|---------|----------|--------------------------|
| Images  | 10 MB    | image/png<br/>image/jpeg |
| Videos  | 50 MB    | video/mp4                |

# PROJECT SUMMARY
This project is a set of microservices for distribution of an initial message with all kinds of services:
Telegram, E-mail or any other service as deemed necessary, including plain HTTP requests.

The idea of the project is to allow a user to set up a project with desirable endpoints and to send a message only once
to distribute it, including any media attached thereto.

The project utilizes [RabbitMQ](https://www.rabbitmq.com/) for message distribution.

The project consists of a receiver microservice to JSON-encode the initial text and attachments, and a dispatcher microservice to push the message into the project-related queues for further processing:

```
                                              --> endpoint microservice #1
                                              |    
incoming message --> receiver --> dispatcher ---> endpoint microservice #2
                                              |
                                              --> endpoint microservice #3 
```

The final distribution is performed by endpoint microservices, each implemented depending on capabilities of the
system used. Use of [RabbitMQ](https://www.rabbitmq.com/) allows to deploy as many clones of an endpoint microservice as
required in case if such channel is used extensively.

[Dashboard](https://github.com/PythonChoker/broker-admin)

Other microservices:

- [Receiver](https://github.com/PythonChoker/broker-receiver)
- [Dispatcher](https://github.com/PythonChoker/broker-dispatcher)
- [SMTP BZ Sender](https://github.com/PythonChoker/broker-smtp-bz)
- [Telegram Sender](https://github.com/PythonChoker/broker-telegram)