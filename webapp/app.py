# Standard library
import os

# Packages
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder


from webapp.views import desktop, server


dir_path = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(dir_path)
templates_dir = os.path.join(app_dir, "templates")

app = FlaskBase(
    __name__,
    "certification.ubuntu.com",
    template_folder=templates_dir,
    static_folder="../static",
    template_404="404.html",
    template_500="500.html",
)

template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)
app.add_url_rule("/desktop", view_func=desktop)
app.add_url_rule("/server", view_func=server)
