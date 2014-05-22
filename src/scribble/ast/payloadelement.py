# payloadelement rather than payloadtype -- it contains both type and annotation
# components


import scrib_util as util


EMPTY_ANNOTATION = 'EMPTY_ANNOTATION'


ANNOTATION_INDEX = 0
PAYLOAD_TYPE_INDEX = 1


def traverse(traverser, node_):
	traversed = []
	traversed.append(traverser.traverse_untyped_leaf(get_annotation_child(node_)))
	traversed.append(traverser.traverse_untyped_leaf(get_type_child(node_)))
	new = util.antlr_dupnode_and_replace_children(node_, traversed)
	return new


def get_annotation(node_):
	return get_annotation_child(node_).getText()

def get_type(node_):
	return get_type_child(node_).getText()


def pretty_print(node_):
	text = ""
	annot = get_annotation(node_)
	if annot != EMPTY_ANNOTATION:
		text = text + get_annotation(node_) + ':'
	text = text + get_type(node_)
	return text


def get_annotation_child(node_):
	return node_.getChild(ANNOTATION_INDEX)

def get_type_child(node_):
	return node_.getChild(PAYLOAD_TYPE_INDEX)
