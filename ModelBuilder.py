import re
from FileModel.FileFragment import FileFragment
from FileModel.FragmentType import FragmentType


class ModelBuilder:
    MiltilineCommentP = r"/\*(?:\n|.)+?\*/"
    LineCommentP = r"//.+?(?:\n|$)"
    IfStatementP = r"[ \t\f]*#[ \t\f]*if\s*.+?(?:\n|$)"
    ElifStatementP = r"[ \t\f]*#[ \t\f]*elif\s*.+?(?:\n|$)"
    ElseStatementP = r"[ \t\f]*#[ \t\f]*else\s*?(?:\n|$)"
    EndIfStatementP = r"[ \t\f]*#[ \t\f]*endif\s*?(?:\n|$)?"

    @staticmethod
    def build(file):
        model = ModelBuilder.split_recursive(file, [
            (ModelBuilder.MiltilineCommentP, FragmentType.Body),
            (ModelBuilder.LineCommentP, FragmentType.Body),
            (ModelBuilder.IfStatementP, FragmentType.IfStatement),
            (ModelBuilder.ElifStatementP, FragmentType.ElIfStatement),
            (ModelBuilder.ElseStatementP, FragmentType.ElseStatement),
            (ModelBuilder.EndIfStatementP, FragmentType.EndIfStatement),
        ])
        return ModelBuilder._normalize(model)

    @staticmethod
    def split_recursive(file, patterns):
        res = [FileFragment(FragmentType.Body, file)]
        left_count = len(patterns)
        if left_count is not 0:
            res = []
            pattern = patterns[0]
            split_result = re.split(str.format("({0})", pattern[0]), file)

            for fragment in split_result:
                if len(fragment) == 0:
                    continue
                if re.match(pattern[0], fragment) is None:
                    res.extend(
                        ModelBuilder.split_recursive(fragment, patterns[1:]))
                else:
                    res.append(FileFragment(pattern[1], fragment))
        return res

    @staticmethod
    def _normalize(model):
        res = []
        body_text = None
        for fragment in model:
            if fragment.type == FragmentType.Body:
                prev_text = body_text if body_text is not None else ''
                body_text = prev_text + fragment.text
            else:
                if body_text is not None:
                    res.append(FileFragment(FragmentType.Body, body_text))
                    body_text = None
                res.append(fragment)
        if body_text is not None:
            res.append(FileFragment(FragmentType.Body, body_text))
        return res
