# Smart B-Roll Detector System Specification

An intelligent, AI-powered video processing pipeline designed to analyze raw footage, multi-cam recordings, or primary A-roll sequences (such as interviews or podcasts) to automatically detect, tag, and extract contextually relevant B-Roll sequences.

---

## Core Detection Engine Logic

The system classifies a video segment as high-quality B-roll by continuously evaluating three main criteria: visual characteristics, audio signals, and semantic context.

### 1. Visual Feature Detection

* **Talking Head Elimination**: The system uses facial landmark detection to isolate frames containing prominent, centered human faces where mouth aspect ratios shift rapidly due to speech. These segments are explicitly tagged as A-Roll and filtered out of the B-roll selection.
* **Shot Boundary Detection**: The engine analyzes color histograms and pixel-intensity shifts between consecutive frames to split long, continuous video files into distinct, independent camera shots.
* **Scene & Object Tagging**: Keyframes from each identified shot are processed through a lightweight vision transformer to apply descriptive metadata tags such as "office", "typing on keyboard", "cityscape", or "close-up".
* **Camera Motion Analysis**: Optical flow algorithms measure movement within the frame to categorize shots into intentional, smooth cinematic motion (like pans, tilts, or tracking shots) versus unstable or shaky footage that should be rejected.

### 2. Audio Signal Analysis

* **Silence & Ambient Profiling**: The audio track is scanned to find segments that lack human speech but contain rich background environmental audio, such as room tone, nature sounds, or traffic.
* **Speech Alignment**: An Automatic Speech Recognition (ASR) model converts spoken audio into text. The system logs the exact timestamps when key topics are discussed to dynamically match them with visual B-roll tags later.

---

## Core Data Structures

To integrate smoothly with professional video editing suites like Adobe Premiere, DaVinci Resolve, or Final Cut Pro, the engine outputs clean, standardized metadata schemas.

### 1. Detected Clip Schema (JSON Format)

The core detection data is structured as a standard JSON object tracking the video ID, frame rate, total duration, and individual clip confidence metrics:
* **videoId**: String identifier for the source file.
* **metadata**: Contains frame rate (e.g., 23.976 fps) and total duration in seconds.
* **detectedBRollClips**: An array of objects tracking each B-roll match. Each object includes a unique clip ID, precise timecode start/end markers, start/end times in seconds, a confidence score (0.0 to 1.0), descriptive content tags, and a visual stability classification (e.g., "smooth_pan").

### 2. Edit Decision List (EDL) Compatibility

The system translates the JSON metadata into a standard Edit Decision List text format. This allows editors to instantly import the markers as a timeline cut list:
* **Title Line**: Identifies the source as a smart B-roll generation output.
* **Timecode Mode**: Declares non-drop frame or drop frame mode.
* **Cut Track Data**: Standardized edit entries mapping the source timecode start/end to the destination timeline timecode start/end, appended with matching content tags for the editing application to read.

---

## Key Advantages & Use Cases

* **Automated Rough Cuts**: Generates a highly accurate timeline of secondary footage immediately after import, saving video editors hours of manual footage scanning.
* **Contextual Dynamic Overlay**: Automatically cross-references and recommends specific asset clips from an internal media library the exact moment a speaker mentions a matching keyword or topic.
* **Social Media Resizing**: Isolates the most visually engaging cinematic segments of a long horizontal video, allowing the system to reframe and crop them into vertical clips for short-form video platforms.
