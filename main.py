from final import create_app
from flask_debugtoolbar import DebugToolbarExtension
# import pytest

app = create_app()
app.app_context().push()


if __name__ == '__main__':
    # toolbar = DebugToolbarExtension(app)
    app.debug = True
    app.run(debug=True)
    # app.config.update({
    #     "TESTING": True,
    # })
