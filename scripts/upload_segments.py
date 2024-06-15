import json

def main():
    segments = [
        {
            "track_id": 1,
            "start": 0,
            "end": 200,
            "mbid": "e6d0ddc5-472a-46a8-b92e-8e49e18429b0",
            "artist": "James Holden",
            "title": "Gone Feral"
        },
        {
            "track_id": 1,
            "start": 115,
            "end": 290,
            "mbid": "bfb8eaa4-7e35-4cec-8989-a297ae8942b2",
            "artist": "96 Back & Text Chunk",
            "title": "Virtual Resonator Dream"
        },
    ]
    s = json.dumps(segments)
    print(s)

if __name__ == '__main__':
    main()