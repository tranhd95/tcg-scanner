# TCG Scanner
A future project for a Trading Card Game card scanner. The motivation behind the project
is to learn about various topics of image processing, know how to implement them and apply 
them to solve a real world problem.

## Idea
I'd like to try to tackle the problem from the most naive solutions to more sophisticated 
methods. Brainstormed ideas below:
- The base of all approaches should be a good preprocessing
  - Detect and crop out the card from the photo (edge detection, polygon detection, ...)
  - Warp it to the real aspect ratio
- Histogram comparison
- Perceptual hashes
  - Hashing the image
  - Hashing the features
- Deep learning (I ran into something called DeepRank?)

## Tech
- Python
- OpenCV

## Sources
https://www.pyimagesearch.com/2019/08/26/building-an-image-hashing-search-engine-with-vp-trees-and-opencv/
