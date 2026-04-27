with open('app/api/routes/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We want to extract the two chat routes:
# @router.get('/{analysis_id}/chat', ...
# ... up to @router.post('/{analysis_id}/export/{format}')

chat_get_match = re.search(r'(@router\.get\(\"\/\{analysis_id\}\/chat\".*?)(?=@router\.post\(\"\/\{analysis_id\}\/export)', content, re.DOTALL)
if chat_get_match:
    chat_code = chat_get_match.group(1)
    
    # Remove it from the original content
    content_without_chat = content.replace(chat_code, '')
    
    # Insert it before get_specific_analysis
    target = r'@router\.get\(\"\/\{project_id\}\/\{analysis_id\}\"'
    target_match = re.search(target, content_without_chat)
    if target_match:
        insert_pos = target_match.start()
        new_content = content_without_chat[:insert_pos] + chat_code + '\n' + content_without_chat[insert_pos:]
        
        with open('app/api/routes/analysis.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('SUCCESS: Moved chat routes above get_specific_analysis')
    else:
        print('ERROR: target not found')
else:
    print('ERROR: chat routes not found')
