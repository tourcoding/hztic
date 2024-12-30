from polyfuzz import PolyFuzz
import jieba

from_list = ["富滇银行股份有限公司丽江宁蒗支行", 
             "中国邮政储蓄银行股份有限公司南京市江宁支行", 
             "广发银行股份有限公司南京江宁支行", 
             "浙商银行南京江宁支行", 
             "江苏紫金农商行江宁开发区支行", 
             "江苏江宁上银村镇银行股份有限公司",
             "杭州银行股份有限公司南京江宁支行",
             "交通银行南京江宁支行",
             "招商银行股份有限公司南京江宁科学园支行",
             "招商银行股份有限公司南京江宁万达支行",
             "招商银行股份有限公司南京江宁支行"]

to_list = ["招商银行南京市江宁支行"]
jieba.suggest_freq("市", True)
jieba.suggest_freq("招商银行", True)
jieba.suggest_freq("中国邮政储蓄银行", True)
jieba.suggest_freq("股份有限公司", True)
jieba.suggest_freq("广发银行", True)
jieba.suggest_freq("杭州银行", True)
jieba.suggest_freq("交通银行", True)
jieba.suggest_freq("江苏江宁上银村镇银行", True)
jieba.suggest_freq("富滇银行", True)
jieba.suggest_freq("江宁支行", True)
jieba.suggest_freq("江宁开发区支行", True)

def tokenize_sentences(sentences):
    return [list(jieba.lcut(sentence)) for sentence in sentences]

from_list = tokenize_sentences(from_list)
to_list = tokenize_sentences(to_list)

model = PolyFuzz("EditDistance")
model.match(from_list, to_list)

print(model.get_matches())
