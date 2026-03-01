import proximitygraphs as pg


def main():
    points = pg.SetPoints.grid(shape=(3, 3))
    mst = pg.MST(points)
    unit_disk = pg.Unit_Disk(points, dist_max=1.01)

    print(f"points: {points.n}")
    print(f"mst edges: {mst.m}")
    print(f"unit disk edges: {unit_disk.m}")
    print(f"unit disk edge list: {unit_disk.graph.get_edgelist()}")


if __name__ == "__main__":
    main()
