from haruka_parser.v2.manager import ContextManager
from urllib.parse import unquote, urljoin
from lxml.html import Element
from haruka_parser.v2.utils.lxml import remove_node, node_to_text
from haruka_parser.v2.doms.base_dom import BaseDom

class LinkDom(BaseDom):
    def __init__(self):
        pass

    def _process(self, node: Element, manager: ContextManager):
        # node_tag = node.tag.lower()
        href = node.get("href")
        if href and not href.startswith(('mailto:', 'tel:', '#', 'javascript:', 'data:')):
            if manager.base_url:
                href = urljoin(manager.base_url, href)
            manager.links.append(href)