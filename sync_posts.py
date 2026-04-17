import json
import requests
import time
import subprocess
import tempfile
from pathlib import Path
from markdownify import markdownify as md

def defuddle_content(html):
    if not html: return ""
    return md(html, strip=['img', 'video']).strip()

def fetch_chunk(topic_id, ids):
    ids_str = '&post_ids[]='.join(map(str, ids))
    url = f'https://forum.level1techs.com/t/{topic_id}/posts.json?post_ids[]={ids_str}'
    r = requests.get(url)
    if r.status_code == 200: return r.json().get('post_stream', {}).get('posts', [])
    return []

def sync_topic(topic_id, file_name):
    file_path = Path(file_name)
    if not file_path.exists():
        print(f"Skipping {topic_id}: {file_name} not found.")
        return

    with open(file_path, 'r') as f:
        primitive = json.load(f)

    existing_ids = {m['post_id'] for m in primitive['data']['mappings']}
    
    print(f"Checking for new posts in topic {topic_id}...")
    r = requests.get(f'https://forum.level1techs.com/t/{topic_id}.json')
    if r.status_code != 200:
        print(f"Failed to fetch metadata for {topic_id}")
        return

    data = r.json()
    stream_ids = data.get('post_stream', {}).get('stream', [])
    new_ids = [pid for pid in stream_ids if pid not in existing_ids]

    if not new_ids:
        print(f"No new posts for topic {topic_id}.")
        return

    print(f"Found {len(new_ids)} new posts for {topic_id}. Fetching...")
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
                'content_markdown': defuddle_content(post.get('cooked')),
                'trust_level': post.get('trust_level'),
                'reply_to_post_number': post.get('reply_to_post_number')
            })
        time.sleep(1)

    primitive['data']['mappings'].extend(new_mappings)
    primitive['data']['mappings'].sort(key=lambda x: x['post_number'])
    primitive['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    with open(file_path, 'w') as f:
        json.dump(primitive, f, indent=2)
    print(f"✓ Added {len(new_mappings)} posts to {file_name}")

def main():
    # Registry of topics to track
    TOPICS = [
        ('247873', 'b70-primitive.json'),
        ('238107', 'intel-arc-proxmox-sriov-primitive.json')
    ]
    
    for tid, fname in TOPICS:
        sync_topic(tid, fname)

if __name__ == '__main__':
    main()
