import { expect, test } from "bun:test"
import type { HighDensityRoute } from "lib/types/high-density-types"
import {
  collectProjectionSegments,
  getNearbySameLayerSegmentPairs,
} from "lib/utils/force-improve-segment-helpers"
import { findNewProperSegmentCrossings } from "lib/utils/high-density-force-improve-topology"

// Grid-router style staircases: many short segments in a small node, the shape
// that made the all-pairs loops dominate force improvement on dense boards.
const createStaircaseRoutes = (
  routeCount: number,
  stepsPerRoute: number,
  seed = 1,
): HighDensityRoute[] => {
  let state = seed
  const random = () => {
    state = (state * 1_103_515_245 + 12_345) % 2_147_483_648
    return state / 2_147_483_648
  }
  return Array.from({ length: routeCount }, (_, routeIndex) => {
    let x = random() * 3
    let y = random() * 2
    const z = routeIndex % 2
    const route = [{ x, y, z }]
    for (let step = 0; step < stepsPerRoute; step += 1) {
      if (random() < 0.5) x += (random() - 0.3) * 0.05
      else y += (random() - 0.3) * 0.05
      route.push({ x, y, z })
    }
    return {
      connectionName: `net${routeIndex}`,
      rootConnectionName: `net${routeIndex}`,
      traceThickness: 0.1,
      viaDiameter: 0.3,
      route,
      vias: [],
    }
  })
}

const bruteForcePairs = (
  routes: HighDensityRoute[],
  margin: number,
): Array<readonly [number, number]> => {
  const segments = collectProjectionSegments(routes)
  const pairs: Array<readonly [number, number]> = []
  for (let left = 0; left < segments.length; left += 1) {
    for (let right = left + 1; right < segments.length; right += 1) {
      const a = segments[left]!
      const b = segments[right]!
      if (
        a.z !== b.z ||
        Math.max(a.start.x, a.end.x) + margin < Math.min(b.start.x, b.end.x) ||
        Math.max(b.start.x, b.end.x) + margin < Math.min(a.start.x, a.end.x) ||
        Math.max(a.start.y, a.end.y) + margin < Math.min(b.start.y, b.end.y) ||
        Math.max(b.start.y, b.end.y) + margin < Math.min(a.start.y, a.end.y)
      ) {
        continue
      }
      pairs.push([left, right])
    }
  }
  return pairs
}

test("segment-pair sweep returns exactly the pairs and order of the nested loops", () => {
  const routes = createStaircaseRoutes(12, 120, 7)
  const segments = collectProjectionSegments(routes)
  for (const margin of [0, 0.1, 0.415]) {
    expect(getNearbySameLayerSegmentPairs(segments, margin, true)).toEqual(
      bruteForcePairs(routes, margin),
    )
    const unordered = getNearbySameLayerSegmentPairs(segments, margin, false)
    expect(
      [...unordered].sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    ).toEqual(bruteForcePairs(routes, margin))
  }
})

test("new-crossing search stays fast on a dense node", () => {
  // 40 routes x 500 steps = 20k segments in a 3 x 2 mm node.
  const original = createStaircaseRoutes(40, 500, 3)
  const moved = structuredClone(original)
  for (const route of moved) {
    for (const point of route.route.slice(1, -1)) point.x += 0.01
  }
  const start = performance.now()
  findNewProperSegmentCrossings(original, moved)
  // Testing all ~2e8 segment pairs took minutes; the sweep takes well under this.
  expect(performance.now() - start).toBeLessThan(10_000)
})
