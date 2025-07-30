from cloe_metadata.utils import templating_engine
from jinja2 import PackageLoader

package_loader = PackageLoader("cloe_sql_transformations.sql", "templates")
env_sql = templating_engine.get_jinja_env(package_loader)
