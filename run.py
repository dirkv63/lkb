import platform
import os
from lkb import create_app, db
from lkb.db_model import User
from waitress import serve


# Run Application
if __name__ == "__main__":
    if platform.node() == "CAA2GKCOR1":
        app = create_app('development')
    else:
        app = create_app('production')

    with app.app_context():
        db.create_all()
        if User.query.filter_by(username='dirk').first() is None:
            User.register('dirk', 'olse')
        if platform.node() == "CAA2GKCOR1":
            # app.run(host="0.0.0.0", port=17501, debug=True)
            app.run()
        else:
            app.run()
            # port = int(os.environ.get("PORT", 8001))
            # serve(app, listen='localhost:8000')
