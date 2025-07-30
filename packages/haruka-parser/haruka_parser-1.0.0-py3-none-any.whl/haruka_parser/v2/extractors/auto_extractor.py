from typing import Dict, Any

from haruka_parser.v2.extractors.base_extractor import BaseExtractor
from haruka_parser.v2.utils.tldextract import extract_domain

from haruka_parser.v2.doms.math_dom import MathDom
from haruka_parser.v2.doms.code_dom import CodeDom
from haruka_parser.v2.doms.table_dom import TableDom
from haruka_parser.v2.doms.media_dom import MediaDom
from haruka_parser.v2.doms.normalize_dom import NormalizeDom
from haruka_parser.v2.doms.useless_dom import UselessDom
from haruka_parser.v2.extractors.title_extractor import TitleExtractor
from haruka_parser.v2.extractors.time_extractor import TimeExtractor
from haruka_parser.v2.doms.turndown_dom import TurndownDom
from haruka_parser.v2.doms.link_dom import LinkDom
from haruka_parser.v2.utils.lxml import iter_node, node_to_text, html_tostring
from haruka_parser.v2.manager import ContextManager
from haruka_parser.v2.config import DROP_TAGS

import traceback
import logging

class AutoExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.math_dom = MathDom()
        self.code_dom = CodeDom()
        self.table_dom = TableDom()
        self.media_dom = MediaDom()
        self.normalize_dom = NormalizeDom()
        self.useless_dom = UselessDom()
        self.link_dom = LinkDom()

        self.turndown_dom = TurndownDom()

        self.title_extractor = TitleExtractor()
        self.time_extractor = TimeExtractor()
        super().__init__()

    def _extract(self, html, **kwargs) -> Dict:
        
        url = kwargs.get("url", "")
        encoding = kwargs.get("encoding", "utf-8")
        use_ftfy = kwargs.get("use_ftfy", False)
        separator = kwargs.get("separator", "\n\n")
        manager = ContextManager(separator=separator, base_url=url)

        # if url:
        #     # 这里有多种选择
        #     # 单独直接处理完成
        #     # 还是用当前解析的 dom 树，做额外操作
        #     # 如果xpath 提取成功，则无需进行启发式规则
        #     domain = extract_domain(url)

        html, manager.encoding = self.read_html(html, encoding)

        tree = self.extract_tree(html)

        if tree is None:
            return
        
        if manager.extract_time and not manager.time:
            try:
                manager.time = self.time_extractor.extract_time(tree)
            except:
                logging.error(f"extract_time error: {traceback.format_exc()}")
        
        # 对于特定网站这里需要插桩处理数据
        # 飞线 ciallo
        self.code_dom.preprocess(html, tree, manager)


        # 删掉无效节点，不包含 script （数学可能有用）
        tree = self.clean_tree(tree)

        self.generate_unique_id(tree, manager)
        
        self.title_extractor.process(tree, manager)
        self.get_base_url(tree, manager)

        # for node in tree.xpath(self.media_dom.xpath):
        #     self.media_dom.process(node, manager)

        for node in iter_node(tree):
            self.title_extractor.fallback_process(node, manager)

            if node.tag not in DROP_TAGS:
                self.math_dom.process(node, manager)
            if node.tag not in DROP_TAGS:
                self.code_dom.process(node, manager)
            if node.tag not in DROP_TAGS:
                self.media_dom.process(node, manager)
            if node.tag not in DROP_TAGS:
                self.table_dom.process(node, manager)
            if node.tag not in DROP_TAGS:
                self.link_dom.process(node, manager)
            if node.tag not in DROP_TAGS:
                self.normalize_dom.process(node, manager)

        # from haruka_parser.v2.utils.lxml import check_unique_id_exists
        # check_unique_id_exists(tree, manager)

        # 到这里希望得到稳定的全文（每行内容确定且不变），并且最好保证合理的多次换行

        # 删除 MANUALLY_CLEANED 比如 script，和一些人工规则
        for node in iter_node(tree):
            self.useless_dom.process(node, manager)

        paragraphs = self.turndown_dom.make_paragraphs(tree, manager)
        self.turndown_dom.attach_dom_meta(paragraphs, manager)

        text_unique_ids = set()
        for paragraph in paragraphs:
            for item in paragraph.items:
                text_unique_ids.add(item.unique_id)

        retained_ids_trafilatura = self.trafilatura_parse(tree, manager) & text_unique_ids
        retained_ids_readability = self.readablity_parse(tree, manager) & text_unique_ids

        self.turndown_dom.set_paragraphs_priority(paragraphs, manager, retained_ids_trafilatura, "traf")
        self.turndown_dom.set_paragraphs_priority(paragraphs, manager, retained_ids_readability, "read")
        
        self.turndown_dom.smart_paragraphs_priority(paragraphs, manager)

        # output_xml = html_tostring(self.turndown_dom.process_tree(tree, manager, retained_ids_trafilatura))

        output_text_full = self.turndown_dom.process_paragraphs(paragraphs, manager)
        output_text_0 = self.turndown_dom.process_paragraphs(paragraphs, manager, lambda x: "traf" in x and "read" in x)
        output_text_1 = self.turndown_dom.process_paragraphs(paragraphs, manager, lambda x: "traf" in x)
        output_text_2 = self.turndown_dom.process_paragraphs(paragraphs, manager, lambda x: "traf" in x or "read" in x)

        if len(output_text_0) < 30:
            output_text = output_text_2
        elif len(output_text_0) / (len(output_text_1)+1) > 0.5:
            output_text = output_text_0
        else:
            output_text = output_text_1

        output_text = self.add_title(output_text, manager)

        output_text = self.text_finalize(output_text, manager)

        if use_ftfy:
            output_text = self.ftfy(output_text)


        if manager.extract_time and not manager.time:
            try:
                manager.time = self.time_extractor.extract_time_from_content(output_text_full)
            except:
                logging.error(f"extract_time error: {traceback.format_exc()}")

        return {
            "text": output_text,
            "paragraphs": self.turndown_dom.paragraphs_todict(paragraphs),
            "dom_attrs": manager.dom_attrs,
            "links": manager.links,
            "title": manager.title,
            "base_url": manager.base_url,
            "time": manager.time,
            "encoding": manager.encoding,
        }


        