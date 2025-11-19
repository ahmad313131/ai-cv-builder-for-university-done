import { setToken, getToken, logout } from "../api";

test("token helpers set/get/remove", () => {
  expect(getToken()).toBeNull();
  setToken("abc");
  expect(getToken()).toBe("abc");
  logout();
  expect(getToken()).toBeNull();
});
