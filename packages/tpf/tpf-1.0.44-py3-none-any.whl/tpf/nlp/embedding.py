import os
import numpy as np
import pandas as pd 
import torch
from torch import nn 

class IndexEmbed(nn.Module):
    def __init__(self, file_pre=None):
        """使用文件保存编码，第二次加载时默认从文件中读取;因为要固定参数，因此不参与梯度计算
        <=10：  2，
        <=100： 3，
        <=1000：4，
        <=100W: 5
        - num_embeddings与embedding_dim不为None时，则手工指定
        - file_pre:最终文件保存格式为 f"embed_{num_embeddings}_{embedding_dim}",为None则表示不记录文件
        
        """
        super().__init__()
        torch.manual_seed(73)
        self.file_pre = file_pre
        with torch.no_grad():
            self._embed2 = self._gen_embedding(num_embeddings=10,     embedding_dim=2,padding_idx=0)
            self._embed3 = self._gen_embedding(num_embeddings=100,    embedding_dim=3,padding_idx=0)
            self._embed4 = self._gen_embedding(num_embeddings=1000,   embedding_dim=4,padding_idx=0)
            self._embed5 = self._gen_embedding(num_embeddings=1000000,embedding_dim=5,padding_idx=0)
        

    def _gen_embedding(self,num_embeddings=8,
                        embedding_dim=3,
                        padding_idx=0):
        using_file = True
        if self.file_pre is None:
            # embed_path = f"embed_{num_embeddings}_{embedding_dim}"
            using_file = False 
        else:
            embed_path = f"{self.file_pre}_{num_embeddings}_{embedding_dim}"
            
        if using_file and os.path.exists(embed_path):
            # 从磁盘加载
            # embedding = joblib.load(embed_path)
            embedding = torch.load(embed_path, weights_only=False)
            return embedding

        with torch.no_grad():
            embedding = nn.Embedding(num_embeddings=num_embeddings,
                            embedding_dim=embedding_dim,
                            padding_idx=padding_idx)

        # joblib.dump(embedding, embed_path)
        if using_file:
            torch.save(embedding, embed_path)
        return embedding


    def embedding(self,data_index, embedding_dim=2, num_embeddings=None):
        """
        - 映射到2，3，4，5维度时固定了最大索引个数，不需要手工指定；相当于固定了最常用的几个映射方法；
        - 若需要更加灵活的方式，指定num_embeddings即可 
        - 所有编码方式都会记录到文件，若存在文件则尤其加载文件
        """
        
        if not isinstance(data_index,torch.Tensor):
            data_index = torch.tensor(data_index)  

        with torch.no_grad():
            if embedding_dim==2:
                embed = self._embed2(data_index)
            elif embedding_dim==3:
                embed = self._embed3(data_index)
            elif embedding_dim==4:
                embed = self._embed4(data_index)
            elif embedding_dim==5:
                embed = self._embed5(data_index)
            elif num_embeddings is not None:
                _embed_model = self._gen_embedding(num_embeddings=num_embeddings, embedding_dim=embedding_dim,padding_idx=0)
                embed = _embed_model(data_index)
        return embed
    
    def forward(self, data_index, embedding_dim=2, num_embeddings=None):
        embed = self.embedding(data_index, embedding_dim=embedding_dim, num_embeddings=num_embeddings)
        return embed
      
class ClsIndexEmbed(nn.Module):
    def __init__(self):
        """类别索引Embedding"""
        super().__init__()
        # 初始化embedding工具
        self._embed = IndexEmbed()

    
    # 定义embedding函数
    def _embed_classify_type(self, indices, embedding_dim=3, num_embeddings=None):
        """定义embedding函数
        """
        indices_array = np.array(indices)
        try:
            embedded = self._embed(indices_array, embedding_dim=embedding_dim, num_embeddings=num_embeddings)
        except  Exception as e:
            print(e)
            print("<=10:2,<=100:3,<=1000:4,<=100W:5,其余需要手工指定embedding_dim，num_embeddings，请检查类别划分是否正确")
        return embedded.tolist()  # 转换为list以便存储在DataFrame中
    
    
    def cls_index_embeding(self, df, cls_dim_dict, num_embeddings=None):
        """将数据表中的类别按指定的维度embedding
        - cls_vec_dict：{'is_feature_value_535': 2}表示将df数表中的is_feature_value_535 embedding到2维向量中
          - 同时删除is_feature_value_535，添加新列，删除旧列
        - 默认规则
          - <=10:2,<=100:3,<=1000:4,<=100W:5,其余需要手工指定embedding_dim，num_embeddings
          - num_embeddings：默认为None时(没有num_embeddings时)走上面的规则，指定具体数字则指定的数字处理
        """
        drop_cols = []
        df_cols = df.columns.tolist()
        for col_name,dim in cls_dim_dict.items():
            if col_name not in df_cols:
                continue 
            # 应用embedding并添加到数据表
            tmp_embedd_col = f"{col_name}_embedded"
            drop_cols.append(tmp_embedd_col)
            df[tmp_embedd_col] = df[col_name].apply(
                lambda x: self._embed_classify_type(x, embedding_dim=dim, num_embeddings=num_embeddings)
            )
            # 将embedding结果拆分成单独的列
            split_cols = []
            for i in range(1,dim+1):
                split_cols.append(f"{col_name}_{i}")
            embedded_cols = pd.DataFrame(
                df[tmp_embedd_col].tolist(),
                columns = split_cols
            )
            df = pd.concat([df, embedded_cols], axis=1)
            drop_cols = [col_name]+drop_cols
        df = df.drop(columns=drop_cols)
        return df 
        
    def forward(self, df, cls_dim_dict, num_embeddings=None):
        """将数据表中存在于cls_dim_dict的类别按指定的维度embedding
        - cls_vec_dict：{'is_feature_value_535': 2}表示将df数表中的is_feature_value_535 embedding到2维向量中
          - 同时删除is_feature_value_535，添加新列，删除旧列
        - 默认规则
          - <=10:2,<=100:3,<=1000:4,<=100W:5,其余需要手工指定embedding_dim，num_embeddings
          - num_embeddings：默认为None时(没有num_embeddings时)走上面的规则，指定具体数字则指定的数字处理

        examples
        ---------------------------------
        from tpf.nlp import ClsIndexEmbed
        cls_dim_dict = {
            'is_feature_value_535': 3,
            'is_feature_value_536': 2
        }

        cie = ClsIndexEmbed()
        df =cie(df,cls_dim_dict)
        
        """
        df = self.cls_index_embeding(df, cls_dim_dict, num_embeddings=num_embeddings)
        return df 
        

