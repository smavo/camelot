import numpy as np

from .cell import Cell


class Table:
    """Table.
    Defines a table object with coordinates relative to a left-bottom
    origin, which is also PDFMiner's coordinate space.

    Parameters
    ----------
    cols : list
        List of tuples representing column x-coordinates in increasing
        order.

    rows : list
        List of tuples representing row y-coordinates in decreasing
        order.

    Attributes
    ----------
    cells : list
        List of cell objects with row-major ordering.

    nocont_ : int
        Number of lines that did not contribute to setting cell edges.
    """

    def __init__(self, cols, rows):

        self.cols = cols
        self.rows = rows
        self.cells = [[Cell(c[0], r[1], c[1], r[0])
                       for c in cols] for r in rows]
        self.nocont_ = 0

    def set_edges(self, vertical, horizontal, jtol=2):
        """Sets a cell's edges to True depending on whether they
        overlap with lines found by imgproc.

        Parameters
        ----------
        vertical : list
            List of vertical lines detected by imgproc. Coordinates
            scaled and translated to the PDFMiner's coordinate space.

        horizontal : list
            List of horizontal lines detected by imgproc. Coordinates
            scaled and translated to the PDFMiner's coordinate space.
        """
        for v in vertical:
            # find closest x coord
            # iterate over y coords and find closest points
            i = [i for i, t in enumerate(self.cols)
                 if np.isclose(v[0], t[0], atol=jtol)]
            j = [j for j, t in enumerate(self.rows)
                 if np.isclose(v[3], t[0], atol=jtol)]
            k = [k for k, t in enumerate(self.rows)
                 if np.isclose(v[1], t[0], atol=jtol)]
            if not j:
                self.nocont_ += 1
                continue
            J = j[0]
            if i == [0]:  # only left edge
                I = i[0]
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[J][I].left = True
                        J += 1
                else:
                    K = len(self.rows)
                    while J < K:
                        self.cells[J][I].left = True
                        J += 1
            elif i == []:  # only right edge
                I = len(self.cols) - 1
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[J][I].right = True
                        J += 1
                else:
                    K = len(self.rows)
                    while J < K:
                        self.cells[J][I].right = True
                        J += 1
            else:  # both left and right edges
                I = i[0]
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[J][I].left = True
                        self.cells[J][I - 1].right = True
                        J += 1
                else:
                    K = len(self.rows)
                    while J < K:
                        self.cells[J][I].left = True
                        self.cells[J][I - 1].right = True
                        J += 1

        for h in horizontal:
            #  find closest y coord
            # iterate over x coords and find closest points
            i = [i for i, t in enumerate(self.rows)
                 if np.isclose(h[1], t[0], atol=jtol)]
            j = [j for j, t in enumerate(self.cols)
                 if np.isclose(h[0], t[0], atol=jtol)]
            k = [k for k, t in enumerate(self.cols)
                 if np.isclose(h[2], t[0], atol=jtol)]
            if not j:
                self.nocont_ += 1
                continue
            J = j[0]
            if i == [0]:  # only top edge
                I = i[0]
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[I][J].top = True
                        J += 1
                else:
                    K = len(self.cols)
                    while J < K:
                        self.cells[I][J].top = True
                        J += 1
            elif i == []:  # only bottom edge
                I = len(self.rows) - 1
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[I][J].bottom = True
                        J += 1
                else:
                    K = len(self.cols)
                    while J < K:
                        self.cells[I][J].bottom = True
                        J += 1
            else:  # both top and bottom edges
                I = i[0]
                if k:
                    K = k[0]
                    while J < K:
                        self.cells[I][J].top = True
                        self.cells[I - 1][J].bottom = True
                        J += 1
                else:
                    K = len(self.cols)
                    while J < K:
                        self.cells[I][J].top = True
                        self.cells[I - 1][J].bottom = True
                        J += 1

        return self

    def set_spanning(self):
        """Sets a cell's spanning_h or spanning_v attribute to True
        depending on whether the cell spans/extends horizontally or
        vertically.
        """
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                bound = self.cells[i][j].get_bounded_edges()
                if bound == 4:
                    continue

                elif bound == 3:
                    if not self.cells[i][j].left:
                        if (self.cells[i][j].right and
                                self.cells[i][j].top and
                                self.cells[i][j].bottom):
                            self.cells[i][j].spanning_h = True

                    elif not self.cells[i][j].right:
                        if (self.cells[i][j].left and
                                self.cells[i][j].top and
                                self.cells[i][j].bottom):
                            self.cells[i][j].spanning_h = True

                    elif not self.cells[i][j].top:
                        if (self.cells[i][j].left and
                                self.cells[i][j].right and
                                self.cells[i][j].bottom):
                            self.cells[i][j].spanning_v = True

                    elif not self.cells[i][j].bottom:
                        if (self.cells[i][j].left and
                                self.cells[i][j].right and
                                self.cells[i][j].top):
                            self.cells[i][j].spanning_v = True

                elif bound == 2:
                    if self.cells[i][j].left and self.cells[i][j].right:
                        if (not self.cells[i][j].top and
                                not self.cells[i][j].bottom):
                            self.cells[i][j].spanning_v = True

                    elif self.cells[i][j].top and self.cells[i][j].bottom:
                        if (not self.cells[i][j].left and
                                not self.cells[i][j].right):
                            self.cells[i][j].spanning_h = True

        return self

    def get_list(self):
        """Returns a two-dimensional list of text assigned to each
        cell.

        Returns
        -------
        ar : list
        """
        ar = []
        for i in range(len(self.cells)):
            ar.append([self.cells[i][j].get_text().strip()
                       for j in range(len(self.cells[i]))])
        return ar