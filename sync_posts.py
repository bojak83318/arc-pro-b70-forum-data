import json
import requests
import time
from pathlib import Path
from markdownify import markdownify as md

def fetch_chunk(topic_id, ids):
    ids_str = '&post_ids[]='.join(map(str, ids))
    url = f'https://forum.level1techs.com/t/{topic_id}/posts.json?post_ids[]={ids_str}'
    r = requests.get(url)
    if r.status_code == 200: return r.json().get('post_stream', {}).get('posts', [])
    return []

def main():
    topic_id = '247873'
    file_path = Path('b70-primitive.json')
    if not file_path.exists(): return
    with open(file_path, 'r') as f: primitive = json.load(f)
    existing_ids = {m['post_id'] for m in primitive['data']['mappings']}
    r = requests.get(f'https://forum.level1techs.com/t/{topic_id}.json')
    if r.status_code != 200: return
    data = r.json()
    stream_ids = data.get('post_stream', {}).get('stream', [])
    new_ids = [pid for pid in stream_ids if pid not in existing_ids]
    if not new_ids: return
    new_mappings = []
    for i in range(0, len(new_ids), 20):
        chunk = new_ids[i:i+20]
        posts = fetch_chunk(topic_id, chunk)
        for post in posts:
            new_mappings.append({
                'username': post.get('username'),
                'post_number': post.get('post_number'),
                'created_at': post.get('created_at'),
                'board': 'Level1Techs Discussion',
                'topic': data.get('title'),
                'post_id': post.get('id'),
                'content_markdown': md(post.get('cooked', \"\"), strip=['img', 'video']).strip(),
                'trust_level': post.get('trust_level'),
                'reply_to_post_number': post.get('reply_to_post_number')
            })
        time.sleep(1)
    primitive['data']['mappings'].extend(new_mappings)
    primitive['data']['mappings'].sort(key=lambda x: x['post_number'])
    primitive['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    primitive['version'] = '1.3.0'
    with open(file_path, 'w') as f: json.dump(primitive, f, indent=2)

if __name__ == '__main__': main()
