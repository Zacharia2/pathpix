import xml.etree.ElementTree as ET
from ebooklib import epub


def create_supermemo_element(parent_element, element_data):
    supermemo_element = ET.SubElement(parent_element, "SuperMemoElement")

    for key, value in element_data.items():
        if key == "SuperMemoElement":
            for sub_element_data in value:
                create_supermemo_element(supermemo_element, sub_element_data)
        elif key == "Content":
            content = ET.SubElement(supermemo_element, "Content")
            for sub_key, sub_value in value.items():
                sub_element = ET.SubElement(content, sub_key)
                sub_element.text = str(sub_value)
        else:
            sub_element = ET.SubElement(supermemo_element, key)
            sub_element.text = str(value)


def create_xml(data):
    root = ET.Element("SuperMemoCollection")

    count = ET.SubElement(root, "Count")
    count.text = str(count_ids(data))

    for element_data in data:
        create_supermemo_element(root, element_data)

    tree = ET.ElementTree(root)
    tree.write("output/11example.xml", encoding="utf-8", xml_declaration=True)


def count_ids(data):
    count = 0
    for item in data:
        if "ID" in item:
            count += 1
        if "SuperMemoElement" in item:
            count += count_ids(item["SuperMemoElement"])
    return count


def get_documents(chapters, Id=1):
    mList = []
    for chapter in chapters:
        # 把这一层处理好，再去处理下一层。
        # 这一层和下一层的逻辑一致。
        if isinstance(chapter, epub.Link):
            Id += 1
            title = chapter.title
            href = chapter.href
            doc = book.get_item_with_href(href)
            if doc:
                Content = {"Question": doc.content.decode("utf-8")}  # 获取文档内容
            else:
                Content = {"Question": ""}
            mList.append(
                {"Title": title, "ID": Id, "Type": "Topic", "Content": Content}
            )
        # 是元组的时候就说明是有子集的数据。这个元组代表当前的数据。元组的内容代表下一层数据。
        # 在元组中，其中第一个元素是本层的数据，第二个元素是下一层的数据，也是入口。
        if isinstance(chapter, tuple):
            Id += 1
            if isinstance(chapter[0], epub.Section):
                title = chapter[0].title
                href = chapter[0].href
                doc = book.get_item_with_href(href)
                # 暂时忽略锚点的情况:'Text/Section0001_0012.xhtml#toc_1
                if doc:
                    Content = {"Question": doc.content.decode("utf-8")}  # 获取文档内容
                else:
                    Content = {"Question": ""}
                element = {
                    "Title": title,
                    "ID": Id,
                    "Type": "Topic",
                    "Content": Content,
                    # "SuperMemoElement": SuperMemoElement,
                }
                mList.append(element)
            # 当元组的第二个元素有子元素的时候。
            if isinstance(chapter[1], list):
                SubElementList = get_documents(chapter[1])
                element["SuperMemoElement"] = SubElementList
    return mList


book = epub.read_epub("epubs/心理学与生活.epub")

res = get_documents(book.toc)

data = []

data.append({"ID": 1, "Title": book.title, "Type": "Concept", "SuperMemoElement": res})

create_xml(data)
