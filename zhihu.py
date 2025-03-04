import random
import re
import time

import requests
import pandas as pd


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


cookie = '_xsrf=UTiINBY61UkGLiwNf1is8I7V9nJV2Vu4; _zap=c162e699-fde7-4454-bd2f-f16f276db141; d_c0=AgDSFRHG3BmPTihglqe0TuBDjOD_TGjCuBA=|1737092601; edu_user_uuid=edu-v1|1fe7d773-0f37-40b1-9bfe-641ea419b977; q_c1=1511377a8adf404f8e9e2a1a7f74990a|1739443071000|1739443071000; z_c0=2|1:0|10:1740117459|4:z_c0|80:MS4xNS0zRlZnQUFBQUFtQUFBQVlBSlZUVDVkb0dqcEhHbjduOTBjRE5iYi1RSEVBY253WjVKX0pBPT0=|3666d07bd22b7d0972d72ca27d4e3473ce0705e9f9cff7509fbdb0f004aecf1a; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1740737422,1740990430,1741055001,1741073954; HMACCOUNT=4A175CAA512C1ABC; __zse_ck=004_sOSWWtNDIjnVPshFO=dDKdIMV52DYCCNIJ8WneiNEwftIZj6qmp39Jcieyp1s9vHYmjzItAhOyL=IYQwdIyDy0JrNpCAJ/kmGOY0W=6di5b/7SGgVsukyUnhLtm4OSqy-OvICBYxqEuQk3HUDKDujrYYhbmL96CutsD15seisRID5JrfH6FGAZgwaiPopA6rUchgun7M8Sg5he6aZyBk3ekDntcRFNIsWAuBlTRVwf52/2dWlmAVE7H0YrEXQRfJo; tst=r; SESSIONID=esubsIoXa4uyoT5iq5MQKpm7YlQUA5Yqfrmi6IGYchx; JOID=UVkXAE7Gfn7xbriWQseKbl17fk5aoQ4KlRvz-huhSAiJB-qhKJfJv5ZquZRFmb17ufSa3yGpZm1An_32e8NaeF0=; osd=UF8TBk7HeHr3brmQRsGKb1t_eE5bpwoMlRr1_h2hSQ6NAeqgLpPPv5dsvZJFmLt_v_Sb2SWvZmxGm_v2esVefl0=; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1741076313; BEC=738c6d0432e7aaf738ea36855cdce904'

url = 'https://www.zhihu.com/api/v4/questions/411884641/feeds?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.author.follower_count%2Cvip_info%2Ckvip_info%2Cbadge%5B*%5D.topics%3Bdata%5B*%5D.settings.table_of_content.enabled&offset=&limit=3&order=default&ws_qiangzhisafe=0&platform=desktop'


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Cookie': cookie
}

def fetch_data(url, headers, min_voteup_count=0, min_comment_count=0, min_follower_count=0, max_items=100):
    answerlist = []
    count = 0
    while True:
        r = requests.get(url, headers=headers).json()
        if r['paging']['is_end'] or count >= max_items:
            break
        for block in r['data']:
            target = block['target']
            if (target.get('voteup_count', 0) >= min_voteup_count and
                target.get('comment_count', 0) >= min_comment_count and
                target['author'].get('follower_count', 0) >= min_follower_count):
                answerlist.append(target['content'])  # content是文本
                print(remove_html_tags(target['content']))
                count += 1
        url = r['paging']['next']
        time.sleep(random.uniform(2, 5))
    return answerlist


if __name__ == '__main__':
    answerlist = fetch_data(url, headers, min_voteup_count=10, min_comment_count=5, min_follower_count=100, max_items=10)
    df = pd.DataFrame(answerlist, columns=['content'])
    df.to_excel('output.xlsx', index=False)