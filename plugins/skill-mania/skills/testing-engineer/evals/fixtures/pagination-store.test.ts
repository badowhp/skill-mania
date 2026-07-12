it("resets the page when the filter changes", () => {
  expect(onFilterChanged({ filter: "open", page: 2 }, "closed")).toEqual({
    filter: "closed",
    page: 1,
  });
});
