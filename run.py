import platform
import os
from lkb import create_app, db
from lkb.db_model import User
from waitress import serve


# Run Application
if __name__ == "__main__":
    app = create_app('development')
    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='dirk').first() is None:
            User.register('dirk', 'olse')
        if platform.node() == "CAA2GKCOR1":
            # app.run(host="0.0.0.0", port=17501, debug=True)
            app.run()
        else:
            port = int(os.environ.get("PORT", 80))
            serve(app, port=port)
