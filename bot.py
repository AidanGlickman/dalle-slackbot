from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
from docarray import Document
import uuid


load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
SERVER_URL = 'grpc://' + os.environ['SERVER_URL']

app = App(token=SLACK_BOT_TOKEN)


@app.event('app_mention')
def mention_handler(body, say):
    prompt = ' '.join(body['event']['text'].split()[1:])
    user = body['event']['user']

    da = Document(text=prompt).post(
        SERVER_URL, parameters={'num_images': 8}).matches
    filename = 'dalle_' + str(uuid.uuid4()) + '.png'
    tmppath = os.path.join(os.sep, 'tmp', filename)
    da.plot_image_sprites(tmppath, fig_size=(10, 10), show_index=True)

    result = app.client.files_upload(
        initial_comment=f'<@{user}> requested: {prompt}',
        channels=body['event']['channel'],
        file=tmppath,
        filename=filename,
        filetype='png')


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
