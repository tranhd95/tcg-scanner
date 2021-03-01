# TCG Scanner

A proof-of-concept project for a Trading Card Game card scanner. The motivation
behind the project is to learn about various topics of image processing, know
how to implement them and apply them to solve a real world problem.

## Current approach

Current approach involves traditional approaches:

1. Detection phase - we want to detect the card in the image and crop it out of
the image. We warp the crop to rectangle.
   - Thresholding
   - Contouring
   - Finding the convex hull
   - Approximate a rectangle shape by Ramer–Douglas–Peucker algorithm
   - Warp by longest edges
2. Search phase - we want to retrieve the card from predefined database. We
achieve this by storing the card hashes and find the most similar ones of the
detected card.
   - Build a database of hashes (we use difference hash) of ground truth cards
   - We hash the detected card and find the most similar hash in our database
      (minimal Hamming's distance)

## Demo

![TCG Scanner Demo](tcg-scanner-demo.webp)

## Future work

- Detection phase with Deep Learning

## Sources

- <https://www.pyimagesearch.com/2019/08/26/building-an-image-hashing-search-engine-with-vp-trees-and-opencv/>
