import {
  API_BASE,
  ENDPOINTS,
  setToken,
  getToken,
  logout,
  uploadPhoto,
  saveCV,
  analyzeCV,
  analyzeCVLLM,
  generateCV,
  downloadCV,
  register,
  login,
  me,
  listCVs,
  getCV,
} from "../api";

const okJson = (data) => ({
  ok: true,
  status: 200,
  text: async () => JSON.stringify(data ?? {}),
  json: async () => data ?? {},
  blob: async () => new Blob(["x"], { type: "application/pdf" }),
});

const errJson = (status = 500, detail = "boom") => ({
  ok: false,
  status,
  text: async () => JSON.stringify({ detail }),
});

beforeEach(() => {
  jest.spyOn(global, "fetch").mockReset();
  // make window.location assign mockable
  delete window.location;
  window.location = { pathname: "/", search: "", assign: jest.fn() };
  localStorage.clear();
});

test("uploadPhoto posts FormData without content-type", async () => {
  global.fetch.mockResolvedValueOnce(okJson({ path: "/uploads/a.jpg" }));
  const file = new File(["img"], "a.jpg", { type: "image/jpeg" });
  const res = await uploadPhoto(file);
  expect(res.path).toBe("/uploads/a.jpg");
  // called correct URL
  expect(global.fetch).toHaveBeenCalledWith(
    ENDPOINTS.upload,
    expect.objectContaining({ method: "POST" })
  );
});

test("saveCV includes bearer token and JSON body", async () => {
  setToken("xyz");
  global.fetch.mockResolvedValueOnce(okJson({ id: 123 }));
  const res = await saveCV({ name: "Alex" });
  expect(getToken()).toBe("xyz");
  expect(res.id).toBe(123);
  const [, init] = global.fetch.mock.calls[0];
  expect(init.headers.Authorization).toBe("Bearer xyz");
  expect(init.headers["Content-Type"]).toBe("application/json");
});

test("analyze endpoints call correct URLs", async () => {
  global.fetch
    .mockResolvedValueOnce(okJson({ score: 70 }))
    .mockResolvedValueOnce(okJson({ score: 72 }));
  const fast = await analyzeCV({ a: 1 });
  const llm = await analyzeCVLLM({ a: 2 });
  expect(fast.score).toBe(70);
  expect(llm.score).toBe(72);
  expect(global.fetch.mock.calls[0][0]).toBe(ENDPOINTS.fast);
  expect(global.fetch.mock.calls[1][0]).toBe(ENDPOINTS.llm);
});

test("generateCV returns blob; downloadCV triggers anchor + URL revoke", async () => {
  global.fetch.mockResolvedValue(okJson());
  // provide URL APIs for JSDOM
  global.URL.createObjectURL = jest.fn(() => "blob://x");
  global.URL.revokeObjectURL = jest.fn();

  const blob = await generateCV({ x: 1 });
  expect(blob).toBeInstanceOf(Blob);

  // mock anchor
  const click = jest.fn();
  jest.spyOn(document, "createElement").mockImplementation(() => ({ click }));

  await downloadCV({ x: 2 }, "cv.pdf");
  expect(click).toHaveBeenCalled();
  expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob://x");
});

test("register & login work; login stores token", async () => {
  global.fetch
    .mockResolvedValueOnce(okJson({ id: 1, email: "a@a.com" })) // register
    .mockResolvedValueOnce(
      okJson({ access_token: "tok", token_type: "bearer" })
    ); // login

  const reg = await register("a@a.com", "p", "alex");
  expect(reg.id).toBe(1);

  const log = await login("a@a.com", "p");
  expect(log.access_token).toBe("tok");
  expect(getToken()).toBe("tok");
});

test("me 401 -> logout and redirect to /login", async () => {
  setToken("will-expire");
  window.location.pathname = "/builder";
  global.fetch.mockResolvedValueOnce(errJson(401, "Unauthorized"));
  await expect(me()).rejects.toThrow("Unauthorized");
  expect(getToken()).toBe(null);
  expect(window.location.assign).toHaveBeenCalled();
  const url = window.location.assign.mock.calls[0][0];
  expect(url).toMatch(/^\/login\?next=/);
});

test("request error surfaces message detail", async () => {
  global.fetch.mockResolvedValueOnce(errJson(503, "Service down"));
  await expect(analyzeCV({})).rejects.toThrow("Service down");
});
