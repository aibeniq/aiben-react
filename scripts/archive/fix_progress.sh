#!/bin/bash
# Fix the stuck progress task directly using Redis CLI

TASK_ID="280048d1-e880-44f4-bdf7-a827b2cdbfcb"
KEY="progress:$TASK_ID"

echo "🔧 Fixing stuck progress task: $TASK_ID"

# Get current data
echo "📊 Current data:"
docker exec aiben-react-redis-1 redis-cli get "$KEY" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
print(f'Status: {data[\"status\"]}')
print(f'Percentage: {data[\"percentage\"]}')
print('Stages:')
for name, stage in data['stages'].items():
    status = '✅' if stage['completed'] else '❌'
    print(f'  {status} {name}: {stage[\"current\"]}/{stage[\"total\"]}')
"

echo ""
echo "🔧 Fixing upload stage..."

# Create fixed JSON - set upload stage as completed
docker exec aiben-react-redis-1 redis-cli get "$KEY" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())

# Fix upload stage
data['stages']['upload']['current'] = data['stages']['upload']['total']
data['stages']['upload']['completed'] = True
data['stages']['upload']['message'] = 'Upload completed successfully'

# Recalculate percentage
total_weight = 0.0
completed_weight = 0.0

for stage in data['stages'].values():
    total_weight += stage['weight']
    if stage['completed']:
        completed_weight += stage['weight']
    else:
        stage_progress = stage['current'] / stage['total'] if stage['total'] > 0 else 0
        completed_weight += stage['weight'] * stage_progress

new_percentage = (completed_weight / total_weight * 100) if total_weight > 0 else 0
data['percentage'] = new_percentage

# Update overall status
all_completed = all(stage['completed'] for stage in data['stages'].values())
data['status'] = 'completed' if all_completed else 'in_progress'

if all_completed:
    data['message'] = f\"{data['operation']} completed successfully\"

print(json.dumps(data))
" > /tmp/fixed_progress.json

# Update Redis with fixed data
echo "💾 Updating Redis..."
docker exec aiben-react-redis-1 redis-cli set "$KEY" "$(cat /tmp/fixed_progress.json)"

echo "✅ Fixed! Verifying..."

# Verify the fix
docker exec aiben-react-redis-1 redis-cli get "$KEY" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
print(f'New Status: {data[\"status\"]}')
print(f'New Percentage: {data[\"percentage\"]}')
print('Updated Stages:')
for name, stage in data['stages'].items():
    status = '✅' if stage['completed'] else '❌'
    print(f'  {status} {name}: {stage[\"current\"]}/{stage[\"total\"]}')
"

echo ""
echo "🎉 Progress task should now be completed!"