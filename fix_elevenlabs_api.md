# Fix ElevenLabs API Key Issue

## Problem
Current API key error: `missing_permissions: text_to_speech`

## Solutions

### Option 1: Get New Free API Key (Recommended)
1. Go to https://elevenlabs.io/
2. Sign up for FREE account (10,000 characters/month)
3. Go to Profile → API Keys
4. Create new API key
5. Replace in `.env` file:
   ```
   ELEVENLABS_API_KEY=your_new_api_key_here
   ```

### Option 2: Use Existing Voices (Free Alternative)
The voice ID `EaBs7G1VibMrNAuz2Na7` might be from a different account or require paid access.

Try these FREE ElevenLabs voices instead:
- `21m00Tcm4TlvDq8ikWAM` - Rachel (Free)
- `AZnzlk1XvdvUeBnXmlld` - Domi (Free)
- `EXAVITQu4vr4xnSDxMaL` - Bella (Free)
- `ErXwobaYiN019PkySvjV` - Antoni (Free)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (Free)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (Free)
- `VR6AewLTigWG4xSOukaG` - Arnold (Free)
- `pNInz6obpgDQGcFmaJgB` - Adam (Free)
- `yoZ06aMxZJJ28mfd3POQ` - Sam (Free)

### Option 3: Quick Test
Replace the voice ID in your code temporarily: