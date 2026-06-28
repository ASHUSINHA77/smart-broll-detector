import unittest

from app.detector import detect_broll_placements


def segment(segment_id, start, end, text):
    return {"id": segment_id, "start": start, "end": end, "text": text}


class DetectorTests(unittest.TestCase):
    def test_excludes_greeting_subscribe_and_signoff(self):
        transcript = {
            "duration": 30,
            "segments": [
                segment("s1", 0, 4, "Welcome back to the vlog from this mountain town."),
                segment("s2", 5, 9, "Subscribe if you like coffee and river trips."),
                segment("s3", 10, 14, "Thanks for watching, see you next time."),
            ],
        }

        self.assertEqual(detect_broll_placements(transcript), [])

    def test_excludes_abstract_reflection_segments(self):
        transcript = {
            "duration": 20,
            "segments": [
                segment("s1", 0, 4, "I feel like the stress was worth it."),
                segment("s2", 5, 9, "Honestly I became a believer in slowing down."),
            ],
        }

        self.assertEqual(detect_broll_placements(transcript), [])

    def test_selects_visual_segments(self):
        transcript = {
            "duration": 30,
            "segments": [
                segment("s1", 0, 4, "We drove past pine forests into a valley."),
                segment("s2", 7, 11, "They were roasting Ethiopian beans near the entrance."),
            ],
        }

        placements = detect_broll_placements(transcript)

        self.assertEqual([item["segment_id"] for item in placements], ["s1", "s2"])
        self.assertIn("forests", placements[0]["reason"])
        self.assertEqual(placements[0]["start"], 0)
        self.assertEqual(placements[0]["end"], 4)

    def test_respects_coverage_cap(self):
        transcript = {
            "duration": 20,
            "segments": [
                segment("s1", 0, 5, "We drove through hills and forest."),
                segment("s2", 8, 13, "We wandered the old town streets."),
            ],
        }

        placements = detect_broll_placements(transcript)

        self.assertEqual(len(placements), 1)
        self.assertLessEqual(sum(item["end"] - item["start"] for item in placements), 8)

    def test_respects_minimum_gap(self):
        transcript = {
            "duration": 30,
            "segments": [
                segment("s1", 0, 4, "We drove through hills and forest."),
                segment("s2", 6, 10, "We wandered the town streets."),
                segment("s3", 14, 18, "We sat on the deck by the river."),
            ],
        }

        placements = detect_broll_placements(transcript)

        self.assertEqual([item["segment_id"] for item in placements], ["s1", "s3"])

    def test_expected_sample_placements(self):
        transcript = {
            "duration": 60,
            "segments": [
                segment("s1", 0, 5, "Welcome back to the channel. Today I am taking you along on a slow coffee day."),
                segment("s2", 6.5, 11.5, "I was feeling pretty stressed this week and needed a reset."),
                segment("s3", 13.5, 19.0, "We drove out past rolling hills, pine forests, and a wide valley."),
                segment("s4", 22.5, 28.0, "At the entrance, a small stall was roasting Ethiopian beans in an old drum."),
                segment("s5", 31.5, 37.0, "I grabbed a mug, sat on the wooden deck, and watched the river while the pour-over cooled."),
                segment("s6", 41.0, 46.5, "After that we wandered through the old town streets and vintage shops."),
                segment("s7", 50.0, 55.0, "This reminded me that the trip was worth it even when plans change."),
                segment("s8", 56.0, 60.0, "Thanks for watching, and see you next time."),
            ],
        }

        placements = detect_broll_placements(transcript)

        self.assertEqual(
            [(item["start"], item["end"]) for item in placements],
            [(13.5, 19.0), (22.5, 28.0), (31.5, 37.0), (41.0, 46.5)],
        )


if __name__ == "__main__":
    unittest.main()
