import pika
import base64
import mimetypes
import json
from flask import Flask, request, jsonify, Response
import werkzeug.exceptions
from configparser import ConfigParser

# Загрузка настроек
config = ConfigParser()
config.read('config.ini')

# Настройка Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.getint(section='APP', option='max_attachment_size') * (1024 * 1024)


# Обработчики ошибок
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def error_handler_attachment_size(e):
    return jsonify({
        'message': f'Размер вложений превышает {config.getint(section='APP', option='max_attachment_size')} MB',
        'status': 422,
    }), 422
# error_handler_attachment_size


@app.route('/', methods=['POST'])
def receive():
    # Валидация запроса
    project_id = f'{request.form.get('project_id')}'
    if project_id is None:
        return jsonify({
            'message': 'Не указан id проекта',
            'status': 422,
        }), 422
    if not (project_id.isdigit() and int(project_id) >= 1):
        return jsonify({
            'message': 'project_id должен быть целым числом больше 1',
            'data': {'project_id': project_id},
            'status': 422,
        }), 422

    text = request.form.get('text')
    attachments = tuple({
        'name': file.filename,
        'mime': mimetypes.guess_type(file.filename)[0],
        'body': base64.b64encode(file.read()).decode(),
    } for file in request.files.getlist('attachments'))

    if len(attachments) < 1 and (text is None or len(text) < 1):
        return jsonify({
            'message': 'Не указано поле text',
            'status': 422,
        }), 422

    max_text_len = config.getint(section='APP', option='max_text_len')
    if len(text) > max_text_len:
        return jsonify({
            'message': f'Превышена максимальная длина текста в {max_text_len} зн.',
            'data': {'text_len': len(text)},
            'status': 422,
        }), 422

    # Подключение к RabbitMQ
    rabbit_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config.get(section='RABBIT', option='host'),
            port=config.getint(section='RABBIT', option='port'),
            credentials=pika.PlainCredentials(
                username=config.get(section='RABBIT', option='user'),
                password=config.get(section='RABBIT', option='password'),
            ),
        )
    )

    message = json.dumps({
        'project_id': project_id,
        'text': text or None,
        'attachments': attachments,
    })

    # Загрузка в RabbitMQ
    rabbit_channel = rabbit_connection.channel()
    rabbit_channel.queue_declare(
        queue=config.get(section='APP', option='queue_dispatcher'),
        durable=True
    )
    rabbit_channel.basic_publish(
        exchange='',
        routing_key=config.get(section='APP', option='queue_dispatcher'),
        body=message,
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
    )
    rabbit_channel.close()

    return jsonify({
        'message': 'Сообщение добавлено в очередь',
        'status': 201,
    }), 201
# receive


app.run(
    host=config.get(section='APP', option='host'),
    port=config.getint(section='APP', option='port'),
    debug=config.getboolean(section='APP', option='debug'),
)
