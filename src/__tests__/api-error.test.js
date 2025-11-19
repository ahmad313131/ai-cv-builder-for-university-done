import { analyzeCV } from "../api";

beforeEach(() => {
  global.fetch = undefined;
});

test("analyzeCV network error throws friendly error", async () => {
  global.fetch = jest.fn().mockRejectedValue(new Error("boom"));
  await expect(analyzeCV({})).rejects.toThrow(/Network error/i);
});
