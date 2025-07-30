var Jn = Object.defineProperty;
var Qn = (e, t, n) => t in e ? Jn(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var x = (e, t, n) => Qn(e, typeof t != "symbol" ? t + "" : t, n);
import * as Yn from "vue";
import { unref as M, watch as z, nextTick as Ne, isRef as Qt, ref as Y, shallowRef as H, watchEffect as Yt, computed as T, toRaw as Xt, customRef as ue, toValue as Ye, readonly as Xn, provide as le, inject as K, shallowReactive as Zn, defineComponent as D, reactive as er, h as $, getCurrentInstance as Zt, renderList as tr, TransitionGroup as en, cloneVNode as Ce, withDirectives as tn, withModifiers as nr, normalizeStyle as rr, normalizeClass as Ve, toDisplayString as xe, vModelDynamic as or, vShow as sr, resolveDynamicComponent as ir, normalizeProps as ar, onErrorCaptured as cr, openBlock as Q, createElementBlock as ne, createElementVNode as nn, createVNode as ur, createCommentVNode as Xe, createBlock as rn, Teleport as lr, renderSlot as fr, toRef as ie, Fragment as on, KeepAlive as dr } from "vue";
let sn;
function hr(e) {
  sn = e;
}
function Ze() {
  return sn;
}
function Ie() {
  const { queryPath: e, pathParams: t, queryParams: n } = Ze();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
const gt = /* @__PURE__ */ new Map();
function pr(e) {
  var t;
  (t = e.scopes) == null || t.forEach((n) => {
    gt.set(n.id, n);
  });
}
function Ge(e) {
  return gt.get(e);
}
function Pe(e) {
  return e && gt.has(e);
}
function ve(e) {
  return typeof e == "function" ? e() : M(e);
}
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const et = () => {
};
function tt(e, t = !1, n = "Timeout") {
  return new Promise((r, o) => {
    setTimeout(t ? () => o(n) : r, e);
  });
}
function nt(e, t = !1) {
  function n(c, { flush: f = "sync", deep: h = !1, timeout: g, throwOnTimeout: m } = {}) {
    let v = null;
    const b = [new Promise((R) => {
      v = z(
        e,
        (N) => {
          c(N) !== t && (v ? v() : Ne(() => v == null ? void 0 : v()), R(N));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return g != null && b.push(
      tt(g, m).then(() => ve(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(b);
  }
  function r(c, f) {
    if (!Qt(c))
      return n((N) => N === c, f);
    const { flush: h = "sync", deep: g = !1, timeout: m, throwOnTimeout: v } = f ?? {};
    let w = null;
    const R = [new Promise((N) => {
      w = z(
        [e, c],
        ([B, U]) => {
          t !== (B === U) && (w ? w() : Ne(() => w == null ? void 0 : w()), N(B));
        },
        {
          flush: h,
          deep: g,
          immediate: !0
        }
      );
    })];
    return m != null && R.push(
      tt(m, v).then(() => ve(e)).finally(() => (w == null || w(), ve(e)))
    ), Promise.race(R);
  }
  function o(c) {
    return n((f) => !!f, c);
  }
  function s(c) {
    return r(null, c);
  }
  function i(c) {
    return r(void 0, c);
  }
  function u(c) {
    return n(Number.isNaN, c);
  }
  function l(c, f) {
    return n((h) => {
      const g = Array.from(h);
      return g.includes(c) || g.includes(ve(c));
    }, f);
  }
  function d(c) {
    return a(1, c);
  }
  function a(c = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= c), f);
  }
  return Array.isArray(ve(e)) ? {
    toMatch: n,
    toContains: l,
    changed: d,
    changedTimes: a,
    get not() {
      return nt(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: o,
    toBeNull: s,
    toBeNaN: u,
    toBeUndefined: i,
    changed: d,
    changedTimes: a,
    get not() {
      return nt(e, !t);
    }
  };
}
function gr(e) {
  return nt(e);
}
function mr(e, t, n) {
  let r;
  Qt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: o = !1,
    evaluating: s = void 0,
    shallow: i = !0,
    onError: u = et
  } = r, l = Y(!o), d = i ? H(t) : Y(t);
  let a = 0;
  return Yt(async (c) => {
    if (!l.value)
      return;
    a++;
    const f = a;
    let h = !1;
    s && Promise.resolve().then(() => {
      s.value = !0;
    });
    try {
      const g = await e((m) => {
        c(() => {
          s && (s.value = !1), h || m();
        });
      });
      f === a && (d.value = g);
    } catch (g) {
      u(g);
    } finally {
      s && f === a && (s.value = !1), h = !0;
    }
  }), o ? T(() => (l.value = !0, d.value)) : d;
}
function vr(e, t, n) {
  const {
    immediate: r = !0,
    delay: o = 0,
    onError: s = et,
    onSuccess: i = et,
    resetOnExecute: u = !0,
    shallow: l = !0,
    throwError: d
  } = {}, a = l ? H(t) : Y(t), c = Y(!1), f = Y(!1), h = H(void 0);
  async function g(w = 0, ...b) {
    u && (a.value = t), h.value = void 0, c.value = !1, f.value = !0, w > 0 && await tt(w);
    const R = typeof e == "function" ? e(...b) : e;
    try {
      const N = await R;
      a.value = N, c.value = !0, i(N);
    } catch (N) {
      if (h.value = N, s(N), d)
        throw N;
    } finally {
      f.value = !1;
    }
    return a.value;
  }
  r && g(o);
  const m = {
    state: a,
    isReady: c,
    isLoading: f,
    error: h,
    execute: g
  };
  function v() {
    return new Promise((w, b) => {
      gr(f).toBe(!1).then(() => w(m)).catch(b);
    });
  }
  return {
    ...m,
    then(w, b) {
      return v().then(w, b);
    }
  };
}
function W(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Yn];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (o) {
    throw new Error(o + " in function code: " + e);
  }
}
function yr(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return W(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function an(e) {
  return e.constructor.name === "AsyncFunction";
}
class _r {
  toString() {
    return "";
  }
}
const be = new _r();
function Re(e) {
  return Xt(e) === be;
}
function wr(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function Er(e) {
  return e[1];
}
function cn(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = un(t, n);
  return e[r];
}
function un(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      if (!t)
        throw new Error("No bindable function provided");
      return t(r[0]);
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function ln(e, t, n) {
  return t.reduce(
    (r, o) => cn(r, o, n),
    e
  );
}
function fn(e, t, n, r) {
  t.reduce((o, s, i) => {
    if (i === t.length - 1)
      o[un(s, r)] = n;
    else
      return cn(o, s, r);
  }, e);
}
function br(e, t, n) {
  const { paths: r, getBindableValueFn: o } = t, { paths: s, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : ue(() => ({
    get() {
      try {
        return ln(
          Ye(e),
          r,
          o
        );
      } catch {
        return;
      }
    },
    set(u) {
      fn(
        Ye(e),
        s || r,
        u,
        i
      );
    }
  }));
}
function mt(e) {
  return ue((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      !Re(e) && JSON.stringify(r) === JSON.stringify(e) || (e = r, n());
    }
  }));
}
function Rr(e, t) {
  const { deepCompare: n = !1 } = e;
  return n ? mt(e.value) : Y(e.value);
}
function Pr(e, t, n) {
  const { bind: r = {}, code: o, const: s = [] } = e, i = Object.values(r).map((a, c) => s[c] === 1 ? a : t.getVueRefObject(a));
  if (an(new Function(o)))
    return mr(
      async () => {
        const a = Object.fromEntries(
          Object.keys(r).map((c, f) => [c, i[f]])
        );
        return await W(o, a)();
      },
      null,
      { lazy: !0 }
    );
  const u = Object.fromEntries(
    Object.keys(r).map((a, c) => [a, i[c]])
  ), l = W(o, u);
  return T(l);
}
function Sr(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? H(t ?? be) : mt(t ?? be);
}
function Or(e, t, n) {
  const {
    inputs: r = [],
    code: o,
    slient: s,
    data: i,
    asyncInit: u = null,
    deepEqOnInput: l = 0
  } = e, d = s || Array(r.length).fill(0), a = i || Array(r.length).fill(0), c = r.filter((v, w) => d[w] === 0 && a[w] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map(
      (v, w) => a[w] === 1 ? v : t.getValue(v)
    );
  }
  const h = W(o), g = l === 0 ? H(be) : mt(be), m = { immediate: !0, deep: !0 };
  return an(h) ? (g.value = u, z(
    c,
    async () => {
      f().some(Re) || (g.value = await h(...f()));
    },
    m
  )) : z(
    c,
    () => {
      const v = f();
      v.some(Re) || (g.value = h(...v));
    },
    m
  ), Xn(g);
}
function kr(e) {
  return e.tag === "vfor";
}
function Nr(e) {
  return e.tag === "vif";
}
function Cr(e) {
  return e.tag === "match";
}
function dn(e) {
  return !("type" in e);
}
function Vr(e) {
  return "type" in e && e.type === "rp";
}
function vt(e) {
  return "sid" in e && "id" in e;
}
class Ir extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function yt(e) {
  return new Ir(e);
}
class Ar {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = Ze().webServerInfo, u = s !== void 0 ? { key: s } : {}, l = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const a = await fetch(l, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: o,
        ...u,
        page: Ie(),
        ...d
      })
    });
    if (!a.ok)
      throw new Error(`HTTP error! status: ${a.status}`);
    return await a.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = Ze().webServerInfo, s = n === "sync" ? o.watch_url : o.watch_async_url, i = t.getServerInputs(), u = {
      key: r,
      input: i,
      page: Ie()
    };
    return await (await fetch(s, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(u)
    })).json();
  }
}
class $r {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = s !== void 0 ? { key: s } : {};
    let u = {};
    const l = {
      bind: n,
      fType: r,
      hKey: o,
      ...i,
      page: Ie(),
      ...u
    };
    return await window.pywebview.api.event_call(l);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = t.getServerInputs(), s = {
      key: r,
      input: o,
      fType: n,
      page: Ie()
    };
    return await window.pywebview.api.watch_call(s);
  }
}
let rt;
function xr(e) {
  switch (e) {
    case "web":
      rt = new Ar();
      break;
    case "webview":
      rt = new $r();
      break;
  }
}
function hn() {
  return rt;
}
var G = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(G || {}), ot = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(ot || {}), ce = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e[e.JsCode = 3] = "JsCode", e))(ce || {});
function Tr(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: ce.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [r, ...t.outputs || []]
  };
}
function pn(e) {
  const { config: t, varGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const [u, l, d] = i, a = n.getVueRefObject(u);
    function c(f, h) {
      const { type: g, value: m } = h;
      if (g === "const") {
        f.value = m;
        return;
      }
      if (g === "action") {
        const v = Dr(m, n);
        f.value = v;
        return;
      }
    }
    return {
      run: () => c(a, l),
      reset: () => c(a, d)
    };
  });
  return {
    run: () => {
      r.forEach((i) => i.run());
    },
    tryReset: () => {
      r.forEach((i) => i.reset());
    }
  };
}
function Dr(e, t) {
  const { inputs: n = [], code: r } = e, o = W(r), s = n.map((i) => t.getValue(i));
  return o(...s);
}
function kt(e) {
  return e == null;
}
function Te(e, t, n) {
  if (kt(t) || kt(e.values))
    return;
  t = t;
  const r = e.values, o = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((s, i) => {
    const u = o[i];
    if (u === 1)
      return;
    if (s.type === ce.Ref) {
      if (u === 2) {
        r[i].forEach(([a, c]) => {
          const f = s.ref, h = {
            ...f,
            path: [...f.path ?? [], ...a]
          };
          n.updateValue(h, c);
        });
        return;
      }
      n.updateValue(s.ref, r[i]);
      return;
    }
    if (s.type === ce.RouterAction) {
      const d = r[i], a = n.getRouter()[d.fn];
      a(...d.args);
      return;
    }
    if (s.type === ce.ElementRefAction) {
      const d = s.ref, a = n.getVueRefObject(d).value, c = r[i], { method: f, args: h = [] } = c;
      a[f](...h);
      return;
    }
    if (s.type === ce.JsCode) {
      const d = r[i];
      if (!d)
        return;
      const a = W(d);
      Promise.resolve(a());
      return;
    }
    const l = n.getVueRefObject(
      s.ref
    );
    l.value = r[i];
  });
}
function jr(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: o } = e;
  return new Mr(t, n, r, o);
}
class Mr {
  constructor(t, n, r, o) {
    x(this, "taskQueue", []);
    x(this, "id2TaskMap", /* @__PURE__ */ new Map());
    x(this, "input2TaskIdMap", yt(() => []));
    this.varMapGetter = r;
    const s = [], i = (u) => {
      var d;
      const l = new Wr(u, r);
      return this.id2TaskMap.set(l.id, l), (d = u.inputs) == null || d.forEach((a, c) => {
        var h, g;
        if (((h = u.data) == null ? void 0 : h[c]) === 0 && ((g = u.slient) == null ? void 0 : g[c]) === 0) {
          if (!dn(a))
            throw new Error("Non-var input bindings are not supported.");
          const m = `${a.sid}-${a.id}`;
          this.input2TaskIdMap.getOrDefault(m).push(l.id);
        }
      }), l;
    };
    t == null || t.forEach((u) => {
      const l = i(u);
      s.push(l);
    }), n == null || n.forEach((u) => {
      const l = i(
        Tr(o, u)
      );
      s.push(l);
    }), s.forEach((u) => {
      const {
        deep: l = !0,
        once: d,
        flush: a,
        immediate: c = !0
      } = u.watchConfig, f = {
        immediate: c,
        deep: l,
        once: d,
        flush: a
      }, h = this._getWatchTargets(u);
      z(
        h,
        (g) => {
          g.some(Re) || (u.modify = !0, this.taskQueue.push(new Br(u)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (s, i) => !r[i] && !n[i]
    ).map((s) => this.varMapGetter.getVueRefObject(s));
  }
  _scheduleNextTick() {
    Ne(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((o) => {
        o.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const o = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (s) => o.has(s.watchTask.id) && s.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!vt(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: o, id: s } = r.ref, i = `${o}-${s}`;
      (this.input2TaskIdMap.get(i) || []).forEach((l) => n.add(l));
    }), n;
  }
}
class Wr {
  constructor(t, n) {
    x(this, "modify", !0);
    x(this, "_running", !1);
    x(this, "id");
    x(this, "_runningPromise", null);
    x(this, "_runningPromiseResolve", null);
    x(this, "_inputInfos");
    this.watchConfig = t, this.varMapGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.varMapGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class Br {
  /**
   *
   */
  constructor(t) {
    x(this, "prevNodes", []);
    x(this, "nextNodes", []);
    x(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await Lr(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function Lr(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, o = pn({
    config: r,
    varGetter: t
  });
  try {
    o.run(), e.taskDone();
    const s = await hn().watchSend(e);
    if (!s)
      return;
    Te(s, n, t);
  } finally {
    o.tryReset();
  }
}
function Nt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function De(e, t) {
  return gn(e, {
    valueFn: t
  });
}
function gn(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([o, s], i) => [
      r ? r(o, s) : o,
      n(s, o, i)
    ])
  );
}
function Fr(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = Ur(t);
  return e[r];
}
function Ur(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Hr(e, t, n) {
  return t.reduce(
    (r, o) => Fr(r, o),
    e
  );
}
function Gr(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const zr = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function mn(e) {
  return typeof e == "function" ? e : zr(Xt(e));
}
function Kr(e, t) {
  const {
    on: n,
    code: r,
    immediate: o,
    deep: s,
    once: i,
    flush: u,
    bind: l = {},
    onData: d,
    bindData: a
  } = e, c = d || Array.from({ length: n.length }).fill(0), f = a || Array.from({ length: Object.keys(l).length }).fill(0), h = De(
    l,
    (v, w, b) => f[b] === 0 ? t.getVueRefObject(v) : v
  ), g = W(r, h), m = n.length === 1 ? Ct(c[0] === 1, n[0], t) : n.map(
    (v, w) => Ct(c[w] === 1, v, t)
  );
  return z(m, g, { immediate: o, deep: s, once: i, flush: u });
}
function Ct(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function qr(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: o,
    data: s,
    code: i,
    immediate: u = !0,
    deep: l,
    once: d,
    flush: a
  } = e, c = o || Array.from({ length: n.length }).fill(0), f = s || Array.from({ length: n.length }).fill(0), h = W(i), g = n.filter((v, w) => c[w] === 0 && f[w] === 0).map((v) => t.getVueRefObject(v));
  function m() {
    return n.map((v, w) => f[w] === 0 ? mn(t.getValue(v)) : v);
  }
  z(
    g,
    () => {
      let v = h(...m());
      if (!r)
        return;
      const b = r.length === 1 ? [v] : v, R = b.map((N) => N === void 0 ? 1 : 0);
      Te(
        {
          values: b,
          types: R
        },
        r,
        t
      );
    },
    { immediate: u, deep: l, once: d, flush: a }
  );
}
const st = yt(() => Symbol());
function Jr(e, t) {
  const n = e.sid, r = st.getOrDefault(n);
  st.set(n, r), le(r, t);
}
function Qr(e) {
  const t = st.get(e);
  return K(t);
}
function Yr() {
  return vn().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function vn() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const Xr = typeof Proxy == "function", Zr = "devtools-plugin:setup", eo = "plugin:settings:set";
let ae, it;
function to() {
  var e;
  return ae !== void 0 || (typeof window < "u" && window.performance ? (ae = !0, it = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (ae = !0, it = globalThis.perf_hooks.performance) : ae = !1), ae;
}
function no() {
  return to() ? it.now() : Date.now();
}
class ro {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const u = t.settings[i];
        r[i] = u.defaultValue;
      }
    const o = `__vue-devtools-plugin-settings__${t.id}`;
    let s = Object.assign({}, r);
    try {
      const i = localStorage.getItem(o), u = JSON.parse(i);
      Object.assign(s, u);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return s;
      },
      setSettings(i) {
        try {
          localStorage.setItem(o, JSON.stringify(i));
        } catch {
        }
        s = i;
      },
      now() {
        return no();
      }
    }, n && n.on(eo, (i, u) => {
      i === this.plugin.id && this.fallbacks.setSettings(u);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, u) => this.target ? this.target.on[u] : (...l) => {
        this.onQueue.push({
          method: u,
          args: l
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, u) => this.target ? this.target[u] : u === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(u) ? (...l) => (this.targetQueue.push({
        method: u,
        args: l,
        resolve: () => {
        }
      }), this.fallbacks[u](...l)) : (...l) => new Promise((d) => {
        this.targetQueue.push({
          method: u,
          args: l,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function oo(e, t) {
  const n = e, r = vn(), o = Yr(), s = Xr && n.enableEarlyProxy;
  if (o && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !s))
    o.emit(Zr, e, t);
  else {
    const i = s ? new ro(n, o) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var P = {};
const J = typeof document < "u";
function yn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function so(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && yn(e.default);
}
const C = Object.assign;
function ze(e, t) {
  const n = {};
  for (const r in t) {
    const o = t[r];
    n[r] = L(o) ? o.map(e) : e(o);
  }
  return n;
}
const we = () => {
}, L = Array.isArray;
function S(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const _n = /#/g, io = /&/g, ao = /\//g, co = /=/g, uo = /\?/g, wn = /\+/g, lo = /%5B/g, fo = /%5D/g, En = /%5E/g, ho = /%60/g, bn = /%7B/g, po = /%7C/g, Rn = /%7D/g, go = /%20/g;
function _t(e) {
  return encodeURI("" + e).replace(po, "|").replace(lo, "[").replace(fo, "]");
}
function mo(e) {
  return _t(e).replace(bn, "{").replace(Rn, "}").replace(En, "^");
}
function at(e) {
  return _t(e).replace(wn, "%2B").replace(go, "+").replace(_n, "%23").replace(io, "%26").replace(ho, "`").replace(bn, "{").replace(Rn, "}").replace(En, "^");
}
function vo(e) {
  return at(e).replace(co, "%3D");
}
function yo(e) {
  return _t(e).replace(_n, "%23").replace(uo, "%3F");
}
function _o(e) {
  return e == null ? "" : yo(e).replace(ao, "%2F");
}
function fe(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    P.NODE_ENV !== "production" && S(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const wo = /\/$/, Eo = (e) => e.replace(wo, "");
function Ke(e, t, n = "/") {
  let r, o = {}, s = "", i = "";
  const u = t.indexOf("#");
  let l = t.indexOf("?");
  return u < l && u >= 0 && (l = -1), l > -1 && (r = t.slice(0, l), s = t.slice(l + 1, u > -1 ? u : t.length), o = e(s)), u > -1 && (r = r || t.slice(0, u), i = t.slice(u, t.length)), r = Po(r ?? t, n), {
    fullPath: r + (s && "?") + s + i,
    path: r,
    query: o,
    hash: fe(i)
  };
}
function bo(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Vt(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function It(e, t, n) {
  const r = t.matched.length - 1, o = n.matched.length - 1;
  return r > -1 && r === o && ee(t.matched[r], n.matched[o]) && Pn(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function ee(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function Pn(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!Ro(e[n], t[n]))
      return !1;
  return !0;
}
function Ro(e, t) {
  return L(e) ? At(e, t) : L(t) ? At(t, e) : e === t;
}
function At(e, t) {
  return L(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function Po(e, t) {
  if (e.startsWith("/"))
    return e;
  if (P.NODE_ENV !== "production" && !t.startsWith("/"))
    return S(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), o = r[r.length - 1];
  (o === ".." || o === ".") && r.push("");
  let s = n.length - 1, i, u;
  for (i = 0; i < r.length; i++)
    if (u = r[i], u !== ".")
      if (u === "..")
        s > 1 && s--;
      else
        break;
  return n.slice(0, s).join("/") + "/" + r.slice(i).join("/");
}
const X = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var de;
(function(e) {
  e.pop = "pop", e.push = "push";
})(de || (de = {}));
var re;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(re || (re = {}));
const qe = "";
function Sn(e) {
  if (!e)
    if (J) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), Eo(e);
}
const So = /^[^#]+#/;
function On(e, t) {
  return e.replace(So, "#") + t;
}
function Oo(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const je = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function ko(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (P.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const s = document.querySelector(e.el);
        if (r && s) {
          S(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        S(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const o = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!o) {
      P.NODE_ENV !== "production" && S(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = Oo(o, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function $t(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const ct = /* @__PURE__ */ new Map();
function No(e, t) {
  ct.set(e, t);
}
function Co(e) {
  const t = ct.get(e);
  return ct.delete(e), t;
}
let Vo = () => location.protocol + "//" + location.host;
function kn(e, t) {
  const { pathname: n, search: r, hash: o } = t, s = e.indexOf("#");
  if (s > -1) {
    let u = o.includes(e.slice(s)) ? e.slice(s).length : 1, l = o.slice(u);
    return l[0] !== "/" && (l = "/" + l), Vt(l, "");
  }
  return Vt(n, e) + r + o;
}
function Io(e, t, n, r) {
  let o = [], s = [], i = null;
  const u = ({ state: f }) => {
    const h = kn(e, location), g = n.value, m = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === g) {
        i = null;
        return;
      }
      v = m ? f.position - m.position : 0;
    } else
      r(h);
    o.forEach((w) => {
      w(n.value, g, {
        delta: v,
        type: de.pop,
        direction: v ? v > 0 ? re.forward : re.back : re.unknown
      });
    });
  };
  function l() {
    i = n.value;
  }
  function d(f) {
    o.push(f);
    const h = () => {
      const g = o.indexOf(f);
      g > -1 && o.splice(g, 1);
    };
    return s.push(h), h;
  }
  function a() {
    const { history: f } = window;
    f.state && f.replaceState(C({}, f.state, { scroll: je() }), "");
  }
  function c() {
    for (const f of s)
      f();
    s = [], window.removeEventListener("popstate", u), window.removeEventListener("beforeunload", a);
  }
  return window.addEventListener("popstate", u), window.addEventListener("beforeunload", a, {
    passive: !0
  }), {
    pauseListeners: l,
    listen: d,
    destroy: c
  };
}
function xt(e, t, n, r = !1, o = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: o ? je() : null
  };
}
function Ao(e) {
  const { history: t, location: n } = window, r = {
    value: kn(e, n)
  }, o = { value: t.state };
  o.value || s(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function s(l, d, a) {
    const c = e.indexOf("#"), f = c > -1 ? (n.host && document.querySelector("base") ? e : e.slice(c)) + l : Vo() + e + l;
    try {
      t[a ? "replaceState" : "pushState"](d, "", f), o.value = d;
    } catch (h) {
      P.NODE_ENV !== "production" ? S("Error with push/replace State", h) : console.error(h), n[a ? "replace" : "assign"](f);
    }
  }
  function i(l, d) {
    const a = C({}, t.state, xt(
      o.value.back,
      // keep back and forward entries but override current position
      l,
      o.value.forward,
      !0
    ), d, { position: o.value.position });
    s(l, a, !0), r.value = l;
  }
  function u(l, d) {
    const a = C(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      o.value,
      t.state,
      {
        forward: l,
        scroll: je()
      }
    );
    P.NODE_ENV !== "production" && !t.state && S(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), s(a.current, a, !0);
    const c = C({}, xt(r.value, l, null), { position: a.position + 1 }, d);
    s(l, c, !1), r.value = l;
  }
  return {
    location: r,
    state: o,
    push: u,
    replace: i
  };
}
function Nn(e) {
  e = Sn(e);
  const t = Ao(e), n = Io(e, t.state, t.location, t.replace);
  function r(s, i = !0) {
    i || n.pauseListeners(), history.go(s);
  }
  const o = C({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: On.bind(null, e)
  }, t, n);
  return Object.defineProperty(o, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(o, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), o;
}
function $o(e = "") {
  let t = [], n = [qe], r = 0;
  e = Sn(e);
  function o(u) {
    r++, r !== n.length && n.splice(r), n.push(u);
  }
  function s(u, l, { direction: d, delta: a }) {
    const c = {
      direction: d,
      delta: a,
      type: de.pop
    };
    for (const f of t)
      f(u, l, c);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: qe,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: On.bind(null, e),
    replace(u) {
      n.splice(r--, 1), o(u);
    },
    push(u, l) {
      o(u);
    },
    listen(u) {
      return t.push(u), () => {
        const l = t.indexOf(u);
        l > -1 && t.splice(l, 1);
      };
    },
    destroy() {
      t = [], n = [qe], r = 0;
    },
    go(u, l = !0) {
      const d = this.location, a = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        u < 0 ? re.back : re.forward
      );
      r = Math.max(0, Math.min(r + u, n.length - 1)), l && s(this.location, d, {
        direction: a,
        delta: u
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function xo(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), P.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && S(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), Nn(e);
}
function Ae(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function Cn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const ut = Symbol(P.NODE_ENV !== "production" ? "navigation failure" : "");
var Tt;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(Tt || (Tt = {}));
const To = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${jo(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function he(e, t) {
  return P.NODE_ENV !== "production" ? C(new Error(To[e](t)), {
    type: e,
    [ut]: !0
  }, t) : C(new Error(), {
    type: e,
    [ut]: !0
  }, t);
}
function q(e, t) {
  return e instanceof Error && ut in e && (t == null || !!(e.type & t));
}
const Do = ["params", "query", "hash"];
function jo(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of Do)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const Dt = "[^/]+?", Mo = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Wo = /[.+*?^${}()[\]/\\]/g;
function Bo(e, t) {
  const n = C({}, Mo, t), r = [];
  let o = n.start ? "^" : "";
  const s = [];
  for (const d of e) {
    const a = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (o += "/");
    for (let c = 0; c < d.length; c++) {
      const f = d[c];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        c || (o += "/"), o += f.value.replace(Wo, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: g, repeatable: m, optional: v, regexp: w } = f;
        s.push({
          name: g,
          repeatable: m,
          optional: v
        });
        const b = w || Dt;
        if (b !== Dt) {
          h += 10;
          try {
            new RegExp(`(${b})`);
          } catch (N) {
            throw new Error(`Invalid custom RegExp for param "${g}" (${b}): ` + N.message);
          }
        }
        let R = m ? `((?:${b})(?:/(?:${b}))*)` : `(${b})`;
        c || (R = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && d.length < 2 ? `(?:/${R})` : "/" + R), v && (R += "?"), o += R, h += 20, v && (h += -8), m && (h += -20), b === ".*" && (h += -50);
      }
      a.push(h);
    }
    r.push(a);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (o += "/?"), n.end ? o += "$" : n.strict && !o.endsWith("/") && (o += "(?:/|$)");
  const i = new RegExp(o, n.sensitive ? "" : "i");
  function u(d) {
    const a = d.match(i), c = {};
    if (!a)
      return null;
    for (let f = 1; f < a.length; f++) {
      const h = a[f] || "", g = s[f - 1];
      c[g.name] = h && g.repeatable ? h.split("/") : h;
    }
    return c;
  }
  function l(d) {
    let a = "", c = !1;
    for (const f of e) {
      (!c || !a.endsWith("/")) && (a += "/"), c = !1;
      for (const h of f)
        if (h.type === 0)
          a += h.value;
        else if (h.type === 1) {
          const { value: g, repeatable: m, optional: v } = h, w = g in d ? d[g] : "";
          if (L(w) && !m)
            throw new Error(`Provided param "${g}" is an array but it is not repeatable (* or + modifiers)`);
          const b = L(w) ? w.join("/") : w;
          if (!b)
            if (v)
              f.length < 2 && (a.endsWith("/") ? a = a.slice(0, -1) : c = !0);
            else
              throw new Error(`Missing required param "${g}"`);
          a += b;
        }
    }
    return a || "/";
  }
  return {
    re: i,
    score: r,
    keys: s,
    parse: u,
    stringify: l
  };
}
function Lo(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Vn(e, t) {
  let n = 0;
  const r = e.score, o = t.score;
  for (; n < r.length && n < o.length; ) {
    const s = Lo(r[n], o[n]);
    if (s)
      return s;
    n++;
  }
  if (Math.abs(o.length - r.length) === 1) {
    if (jt(r))
      return 1;
    if (jt(o))
      return -1;
  }
  return o.length - r.length;
}
function jt(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Fo = {
  type: 0,
  value: ""
}, Uo = /[a-zA-Z0-9_]/;
function Ho(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Fo]];
  if (!e.startsWith("/"))
    throw new Error(P.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const o = [];
  let s;
  function i() {
    s && o.push(s), s = [];
  }
  let u = 0, l, d = "", a = "";
  function c() {
    d && (n === 0 ? s.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (s.length > 1 && (l === "*" || l === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), s.push({
      type: 1,
      value: d,
      regexp: a,
      repeatable: l === "*" || l === "+",
      optional: l === "*" || l === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += l;
  }
  for (; u < e.length; ) {
    if (l = e[u++], l === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        l === "/" ? (d && c(), i()) : l === ":" ? (c(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        l === "(" ? n = 2 : Uo.test(l) ? f() : (c(), n = 0, l !== "*" && l !== "?" && l !== "+" && u--);
        break;
      case 2:
        l === ")" ? a[a.length - 1] == "\\" ? a = a.slice(0, -1) + l : n = 3 : a += l;
        break;
      case 3:
        c(), n = 0, l !== "*" && l !== "?" && l !== "+" && u--, a = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), c(), i(), o;
}
function Go(e, t, n) {
  const r = Bo(Ho(e.path), n);
  if (P.NODE_ENV !== "production") {
    const s = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      s.has(i.name) && S(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), s.add(i.name);
  }
  const o = C(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !o.record.aliasOf == !t.record.aliasOf && t.children.push(o), o;
}
function zo(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = Lt({ strict: !1, end: !0, sensitive: !1 }, t);
  function o(c) {
    return r.get(c);
  }
  function s(c, f, h) {
    const g = !h, m = Wt(c);
    P.NODE_ENV !== "production" && Qo(m, f), m.aliasOf = h && h.record;
    const v = Lt(t, c), w = [m];
    if ("alias" in c) {
      const N = typeof c.alias == "string" ? [c.alias] : c.alias;
      for (const B of N)
        w.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          Wt(C({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: B,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let b, R;
    for (const N of w) {
      const { path: B } = N;
      if (f && B[0] !== "/") {
        const U = f.record.path, F = U[U.length - 1] === "/" ? "" : "/";
        N.path = f.record.path + (B && F + B);
      }
      if (P.NODE_ENV !== "production" && N.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (b = Go(N, f, v), P.NODE_ENV !== "production" && f && B[0] === "/" && Xo(b, f), h ? (h.alias.push(b), P.NODE_ENV !== "production" && Jo(h, b)) : (R = R || b, R !== b && R.alias.push(b), g && c.name && !Bt(b) && (P.NODE_ENV !== "production" && Yo(c, f), i(c.name))), In(b) && l(b), m.children) {
        const U = m.children;
        for (let F = 0; F < U.length; F++)
          s(U[F], b, h && h.children[F]);
      }
      h = h || b;
    }
    return R ? () => {
      i(R);
    } : we;
  }
  function i(c) {
    if (Cn(c)) {
      const f = r.get(c);
      f && (r.delete(c), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(c);
      f > -1 && (n.splice(f, 1), c.record.name && r.delete(c.record.name), c.children.forEach(i), c.alias.forEach(i));
    }
  }
  function u() {
    return n;
  }
  function l(c) {
    const f = Zo(c, n);
    n.splice(f, 0, c), c.record.name && !Bt(c) && r.set(c.record.name, c);
  }
  function d(c, f) {
    let h, g = {}, m, v;
    if ("name" in c && c.name) {
      if (h = r.get(c.name), !h)
        throw he(1, {
          location: c
        });
      if (P.NODE_ENV !== "production") {
        const R = Object.keys(c.params || {}).filter((N) => !h.keys.find((B) => B.name === N));
        R.length && S(`Discarded invalid param(s) "${R.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, g = C(
        // paramsFromLocation is a new object
        Mt(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((R) => !R.optional).concat(h.parent ? h.parent.keys.filter((R) => R.optional) : []).map((R) => R.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        c.params && Mt(c.params, h.keys.map((R) => R.name))
      ), m = h.stringify(g);
    } else if (c.path != null)
      m = c.path, P.NODE_ENV !== "production" && !m.startsWith("/") && S(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((R) => R.re.test(m)), h && (g = h.parse(m), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((R) => R.re.test(f.path)), !h)
        throw he(1, {
          location: c,
          currentLocation: f
        });
      v = h.record.name, g = C({}, f.params, c.params), m = h.stringify(g);
    }
    const w = [];
    let b = h;
    for (; b; )
      w.unshift(b.record), b = b.parent;
    return {
      name: v,
      path: m,
      params: g,
      matched: w,
      meta: qo(w)
    };
  }
  e.forEach((c) => s(c));
  function a() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: s,
    resolve: d,
    removeRoute: i,
    clearRoutes: a,
    getRoutes: u,
    getRecordMatcher: o
  };
}
function Mt(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function Wt(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Ko(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Ko(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function Bt(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function qo(e) {
  return e.reduce((t, n) => C(t, n.meta), {});
}
function Lt(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function lt(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Jo(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(lt.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(lt.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function Qo(e, t) {
  t && t.record.name && !e.name && !e.path && S(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function Yo(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function Xo(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(lt.bind(null, n)))
      return S(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function Zo(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const s = n + r >> 1;
    Vn(e, t[s]) < 0 ? r = s : n = s + 1;
  }
  const o = es(e);
  return o && (r = t.lastIndexOf(o, r - 1), P.NODE_ENV !== "production" && r < 0 && S(`Finding ancestor route "${o.record.path}" failed for "${e.record.path}"`)), r;
}
function es(e) {
  let t = e;
  for (; t = t.parent; )
    if (In(t) && Vn(e, t) === 0)
      return t;
}
function In({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function ts(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let o = 0; o < r.length; ++o) {
    const s = r[o].replace(wn, " "), i = s.indexOf("="), u = fe(i < 0 ? s : s.slice(0, i)), l = i < 0 ? null : fe(s.slice(i + 1));
    if (u in t) {
      let d = t[u];
      L(d) || (d = t[u] = [d]), d.push(l);
    } else
      t[u] = l;
  }
  return t;
}
function Ft(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = vo(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (L(r) ? r.map((s) => s && at(s)) : [r && at(r)]).forEach((s) => {
      s !== void 0 && (t += (t.length ? "&" : "") + n, s != null && (t += "=" + s));
    });
  }
  return t;
}
function ns(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = L(r) ? r.map((o) => o == null ? null : "" + o) : r == null ? r : "" + r);
  }
  return t;
}
const rs = Symbol(P.NODE_ENV !== "production" ? "router view location matched" : ""), Ut = Symbol(P.NODE_ENV !== "production" ? "router view depth" : ""), Me = Symbol(P.NODE_ENV !== "production" ? "router" : ""), wt = Symbol(P.NODE_ENV !== "production" ? "route location" : ""), ft = Symbol(P.NODE_ENV !== "production" ? "router view location" : "");
function ye() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const o = e.indexOf(r);
      o > -1 && e.splice(o, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function Z(e, t, n, r, o, s = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[o] = r.enterCallbacks[o] || []);
  return () => new Promise((u, l) => {
    const d = (f) => {
      f === !1 ? l(he(4, {
        from: n,
        to: t
      })) : f instanceof Error ? l(f) : Ae(f) ? l(he(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[o] === i && typeof f == "function" && i.push(f), u());
    }, a = s(() => e.call(r && r.instances[o], t, n, P.NODE_ENV !== "production" ? os(d, t, n) : d));
    let c = Promise.resolve(a);
    if (e.length < 3 && (c = c.then(d)), P.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof a == "object" && "then" in a)
        c = c.then((h) => d._called ? h : (S(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (a !== void 0 && !d._called) {
        S(f), l(new Error("Invalid navigation guard"));
        return;
      }
    }
    c.catch((f) => l(f));
  });
}
function os(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && S(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function Je(e, t, n, r, o = (s) => s()) {
  const s = [];
  for (const i of e) {
    P.NODE_ENV !== "production" && !i.components && !i.children.length && S(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const u in i.components) {
      let l = i.components[u];
      if (P.NODE_ENV !== "production") {
        if (!l || typeof l != "object" && typeof l != "function")
          throw S(`Component "${u}" in record with path "${i.path}" is not a valid component. Received "${String(l)}".`), new Error("Invalid route component");
        if ("then" in l) {
          S(`Component "${u}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = l;
          l = () => d;
        } else l.__asyncLoader && // warn only once per component
        !l.__warnedDefineAsync && (l.__warnedDefineAsync = !0, S(`Component "${u}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[u]))
        if (yn(l)) {
          const a = (l.__vccOpts || l)[t];
          a && s.push(Z(a, n, r, i, u, o));
        } else {
          let d = l();
          P.NODE_ENV !== "production" && !("catch" in d) && (S(`Component "${u}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), s.push(() => d.then((a) => {
            if (!a)
              throw new Error(`Couldn't resolve component "${u}" at "${i.path}"`);
            const c = so(a) ? a.default : a;
            i.mods[u] = a, i.components[u] = c;
            const h = (c.__vccOpts || c)[t];
            return h && Z(h, n, r, i, u, o)();
          }));
        }
    }
  }
  return s;
}
function Ht(e) {
  const t = K(Me), n = K(wt);
  let r = !1, o = null;
  const s = T(() => {
    const a = M(e.to);
    return P.NODE_ENV !== "production" && (!r || a !== o) && (Ae(a) || (r ? S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- previous to:`, o, `
- props:`, e) : S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- props:`, e)), o = a, r = !0), t.resolve(a);
  }), i = T(() => {
    const { matched: a } = s.value, { length: c } = a, f = a[c - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const g = h.findIndex(ee.bind(null, f));
    if (g > -1)
      return g;
    const m = Gt(a[c - 2]);
    return (
      // we are dealing with nested routes
      c > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      Gt(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(ee.bind(null, a[c - 2])) : g
    );
  }), u = T(() => i.value > -1 && us(n.params, s.value.params)), l = T(() => i.value > -1 && i.value === n.matched.length - 1 && Pn(n.params, s.value.params));
  function d(a = {}) {
    if (cs(a)) {
      const c = t[M(e.replace) ? "replace" : "push"](
        M(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(we);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => c), c;
    }
    return Promise.resolve();
  }
  if (P.NODE_ENV !== "production" && J) {
    const a = Zt();
    if (a) {
      const c = {
        route: s.value,
        isActive: u.value,
        isExactActive: l.value,
        error: null
      };
      a.__vrl_devtools = a.__vrl_devtools || [], a.__vrl_devtools.push(c), Yt(() => {
        c.route = s.value, c.isActive = u.value, c.isExactActive = l.value, c.error = Ae(M(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: s,
    href: T(() => s.value.href),
    isActive: u,
    isExactActive: l,
    navigate: d
  };
}
function ss(e) {
  return e.length === 1 ? e[0] : e;
}
const is = /* @__PURE__ */ D({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: Ht,
  setup(e, { slots: t }) {
    const n = er(Ht(e)), { options: r } = K(Me), o = T(() => ({
      [zt(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [zt(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const s = t.default && ss(t.default(n));
      return e.custom ? s : $("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: o.value
      }, s);
    };
  }
}), as = is;
function cs(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function us(e, t) {
  for (const n in t) {
    const r = t[n], o = e[n];
    if (typeof r == "string") {
      if (r !== o)
        return !1;
    } else if (!L(o) || o.length !== r.length || r.some((s, i) => s !== o[i]))
      return !1;
  }
  return !0;
}
function Gt(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const zt = (e, t, n) => e ?? t ?? n, ls = /* @__PURE__ */ D({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    P.NODE_ENV !== "production" && ds();
    const r = K(ft), o = T(() => e.route || r.value), s = K(Ut, 0), i = T(() => {
      let d = M(s);
      const { matched: a } = o.value;
      let c;
      for (; (c = a[d]) && !c.components; )
        d++;
      return d;
    }), u = T(() => o.value.matched[i.value]);
    le(Ut, T(() => i.value + 1)), le(rs, u), le(ft, o);
    const l = Y();
    return z(() => [l.value, u.value, e.name], ([d, a, c], [f, h, g]) => {
      a && (a.instances[c] = d, h && h !== a && d && d === f && (a.leaveGuards.size || (a.leaveGuards = h.leaveGuards), a.updateGuards.size || (a.updateGuards = h.updateGuards))), d && a && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !ee(a, h) || !f) && (a.enterCallbacks[c] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = o.value, a = e.name, c = u.value, f = c && c.components[a];
      if (!f)
        return Kt(n.default, { Component: f, route: d });
      const h = c.props[a], g = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = $(f, C({}, g, t, {
        onVnodeUnmounted: (w) => {
          w.component.isUnmounted && (c.instances[a] = null);
        },
        ref: l
      }));
      if (P.NODE_ENV !== "production" && J && v.ref) {
        const w = {
          depth: i.value,
          name: c.name,
          path: c.path,
          meta: c.meta
        };
        (L(v.ref) ? v.ref.map((R) => R.i) : [v.ref.i]).forEach((R) => {
          R.__vrv_devtools = w;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        Kt(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function Kt(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const fs = ls;
function ds() {
  const e = Zt(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    S(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function _e(e, t) {
  const n = C({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => Rs(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function ke(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let hs = 0;
function ps(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = hs++;
  oo({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (o) => {
    typeof o.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), o.on.inspectComponent((a, c) => {
      a.instanceData && a.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: _e(t.currentRoute.value, "Current Route")
      });
    }), o.on.visitComponentTree(({ treeNode: a, componentInstance: c }) => {
      if (c.__vrv_devtools) {
        const f = c.__vrv_devtools;
        a.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: An
        });
      }
      L(c.__vrl_devtools) && (c.__devtoolsApi = o, c.__vrl_devtools.forEach((f) => {
        let h = f.route.path, g = Tn, m = "", v = 0;
        f.error ? (h = f.error, g = _s, v = ws) : f.isExactActive ? (g = xn, m = "This is exactly active") : f.isActive && (g = $n, m = "This link is active"), a.tags.push({
          label: h,
          textColor: v,
          tooltip: m,
          backgroundColor: g
        });
      }));
    }), z(t.currentRoute, () => {
      l(), o.notifyComponentUpdate(), o.sendInspectorTree(u), o.sendInspectorState(u);
    });
    const s = "router:navigations:" + r;
    o.addTimelineLayer({
      id: s,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((a, c) => {
      o.addTimelineEvent({
        layerId: s,
        event: {
          title: "Error during Navigation",
          subtitle: c.fullPath,
          logType: "error",
          time: o.now(),
          data: { error: a },
          groupId: c.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((a, c) => {
      const f = {
        guard: ke("beforeEach"),
        from: _e(c, "Current Location during this navigation"),
        to: _e(a, "Target location")
      };
      Object.defineProperty(a.meta, "__navigationId", {
        value: i++
      }), o.addTimelineEvent({
        layerId: s,
        event: {
          time: o.now(),
          title: "Start of navigation",
          subtitle: a.fullPath,
          data: f,
          groupId: a.meta.__navigationId
        }
      });
    }), t.afterEach((a, c, f) => {
      const h = {
        guard: ke("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = ke("❌")) : h.status = ke("✅"), h.from = _e(c, "Current Location during this navigation"), h.to = _e(a, "Target location"), o.addTimelineEvent({
        layerId: s,
        event: {
          title: "End of navigation",
          subtitle: a.fullPath,
          time: o.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: a.meta.__navigationId
        }
      });
    });
    const u = "router-inspector:" + r;
    o.addInspector({
      id: u,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function l() {
      if (!d)
        return;
      const a = d;
      let c = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      c.forEach(Mn), a.filter && (c = c.filter((f) => (
        // save matches state based on the payload
        dt(f, a.filter.toLowerCase())
      ))), c.forEach((f) => jn(f, t.currentRoute.value)), a.rootNodes = c.map(Dn);
    }
    let d;
    o.on.getInspectorTree((a) => {
      d = a, a.app === e && a.inspectorId === u && l();
    }), o.on.getInspectorState((a) => {
      if (a.app === e && a.inspectorId === u) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === a.nodeId);
        f && (a.state = {
          options: ms(f)
        });
      }
    }), o.sendInspectorTree(u), o.sendInspectorState(u);
  });
}
function gs(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function ms(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${gs(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const An = 15485081, $n = 2450411, xn = 8702998, vs = 2282478, Tn = 16486972, ys = 6710886, _s = 16704226, ws = 12131356;
function Dn(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: vs
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: Tn
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: An
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: xn
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: $n
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: ys
  });
  let r = n.__vd_id;
  return r == null && (r = String(Es++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(Dn)
  };
}
let Es = 0;
const bs = /^\/(.*)\/([a-z]*)$/;
function jn(e, t) {
  const n = t.matched.length && ee(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => ee(r, e.record))), e.children.forEach((r) => jn(r, t));
}
function Mn(e) {
  e.__vd_match = !1, e.children.forEach(Mn);
}
function dt(e, t) {
  const n = String(e.re).match(bs);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => dt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const o = e.record.path.toLowerCase(), s = fe(o);
  return !t.startsWith("/") && (s.includes(t) || o.includes(t)) || s.startsWith(t) || o.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => dt(i, t));
}
function Rs(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function Ps(e) {
  const t = zo(e.routes, e), n = e.parseQuery || ts, r = e.stringifyQuery || Ft, o = e.history;
  if (P.NODE_ENV !== "production" && !o)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const s = ye(), i = ye(), u = ye(), l = H(X);
  let d = X;
  J && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const a = ze.bind(null, (p) => "" + p), c = ze.bind(null, _o), f = (
    // @ts-expect-error: intentionally avoid the type check
    ze.bind(null, fe)
  );
  function h(p, _) {
    let y, E;
    return Cn(p) ? (y = t.getRecordMatcher(p), P.NODE_ENV !== "production" && !y && S(`Parent route "${String(p)}" not found when adding child route`, _), E = _) : E = p, t.addRoute(E, y);
  }
  function g(p) {
    const _ = t.getRecordMatcher(p);
    _ ? t.removeRoute(_) : P.NODE_ENV !== "production" && S(`Cannot remove non-existent route "${String(p)}"`);
  }
  function m() {
    return t.getRoutes().map((p) => p.record);
  }
  function v(p) {
    return !!t.getRecordMatcher(p);
  }
  function w(p, _) {
    if (_ = C({}, _ || l.value), typeof p == "string") {
      const O = Ke(n, p, _.path), I = t.resolve({ path: O.path }, _), te = o.createHref(O.fullPath);
      return P.NODE_ENV !== "production" && (te.startsWith("//") ? S(`Location "${p}" resolved to "${te}". A resolved location cannot start with multiple slashes.`) : I.matched.length || S(`No match found for location with path "${p}"`)), C(O, I, {
        params: f(I.params),
        hash: fe(O.hash),
        redirectedFrom: void 0,
        href: te
      });
    }
    if (P.NODE_ENV !== "production" && !Ae(p))
      return S(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), w({});
    let y;
    if (p.path != null)
      P.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && S(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), y = C({}, p, {
        path: Ke(n, p.path, _.path).path
      });
    else {
      const O = C({}, p.params);
      for (const I in O)
        O[I] == null && delete O[I];
      y = C({}, p, {
        params: c(O)
      }), _.params = c(_.params);
    }
    const E = t.resolve(y, _), V = p.hash || "";
    P.NODE_ENV !== "production" && V && !V.startsWith("#") && S(`A \`hash\` should always start with the character "#". Replace "${V}" with "#${V}".`), E.params = a(f(E.params));
    const A = bo(r, C({}, p, {
      hash: mo(V),
      path: E.path
    })), k = o.createHref(A);
    return P.NODE_ENV !== "production" && (k.startsWith("//") ? S(`Location "${p}" resolved to "${k}". A resolved location cannot start with multiple slashes.`) : E.matched.length || S(`No match found for location with path "${p.path != null ? p.path : p}"`)), C({
      fullPath: A,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: V,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === Ft ? ns(p.query) : p.query || {}
      )
    }, E, {
      redirectedFrom: void 0,
      href: k
    });
  }
  function b(p) {
    return typeof p == "string" ? Ke(n, p, l.value.path) : C({}, p);
  }
  function R(p, _) {
    if (d !== p)
      return he(8, {
        from: _,
        to: p
      });
  }
  function N(p) {
    return F(p);
  }
  function B(p) {
    return N(C(b(p), { replace: !0 }));
  }
  function U(p) {
    const _ = p.matched[p.matched.length - 1];
    if (_ && _.redirect) {
      const { redirect: y } = _;
      let E = typeof y == "function" ? y(p) : y;
      if (typeof E == "string" && (E = E.includes("?") || E.includes("#") ? E = b(E) : (
        // force empty params
        { path: E }
      ), E.params = {}), P.NODE_ENV !== "production" && E.path == null && !("name" in E))
        throw S(`Invalid redirect found:
${JSON.stringify(E, null, 2)}
 when navigating to "${p.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return C({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: E.path != null ? {} : p.params
      }, E);
    }
  }
  function F(p, _) {
    const y = d = w(p), E = l.value, V = p.state, A = p.force, k = p.replace === !0, O = U(y);
    if (O)
      return F(
        C(b(O), {
          state: typeof O == "object" ? C({}, V, O.state) : V,
          force: A,
          replace: k
        }),
        // keep original redirectedFrom if it exists
        _ || y
      );
    const I = y;
    I.redirectedFrom = _;
    let te;
    return !A && It(r, E, y) && (te = he(16, { to: I, from: E }), St(
      E,
      E,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (te ? Promise.resolve(te) : Et(I, E)).catch((j) => q(j) ? (
      // navigation redirects still mark the router as ready
      q(
        j,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? j : Fe(j)
    ) : (
      // reject any unknown error
      Le(j, I, E)
    )).then((j) => {
      if (j) {
        if (q(
          j,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return P.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          It(r, w(j.to), I) && // and we have done it a couple of times
          _ && // @ts-expect-error: added only in dev
          (_._count = _._count ? (
            // @ts-expect-error
            _._count + 1
          ) : 1) > 30 ? (S(`Detected a possibly infinite redirection in a navigation guard when going from "${E.fullPath}" to "${I.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : F(
            // keep options
            C({
              // preserve an existing replacement but allow the redirect to override it
              replace: k
            }, b(j.to), {
              state: typeof j.to == "object" ? C({}, V, j.to.state) : V,
              force: A
            }),
            // preserve the original redirectedFrom if any
            _ || I
          );
      } else
        j = Rt(I, E, !0, k, V);
      return bt(I, E, j), j;
    });
  }
  function zn(p, _) {
    const y = R(p, _);
    return y ? Promise.reject(y) : Promise.resolve();
  }
  function We(p) {
    const _ = Oe.values().next().value;
    return _ && typeof _.runWithContext == "function" ? _.runWithContext(p) : p();
  }
  function Et(p, _) {
    let y;
    const [E, V, A] = Ss(p, _);
    y = Je(E.reverse(), "beforeRouteLeave", p, _);
    for (const O of E)
      O.leaveGuards.forEach((I) => {
        y.push(Z(I, p, _));
      });
    const k = zn.bind(null, p, _);
    return y.push(k), se(y).then(() => {
      y = [];
      for (const O of s.list())
        y.push(Z(O, p, _));
      return y.push(k), se(y);
    }).then(() => {
      y = Je(V, "beforeRouteUpdate", p, _);
      for (const O of V)
        O.updateGuards.forEach((I) => {
          y.push(Z(I, p, _));
        });
      return y.push(k), se(y);
    }).then(() => {
      y = [];
      for (const O of A)
        if (O.beforeEnter)
          if (L(O.beforeEnter))
            for (const I of O.beforeEnter)
              y.push(Z(I, p, _));
          else
            y.push(Z(O.beforeEnter, p, _));
      return y.push(k), se(y);
    }).then(() => (p.matched.forEach((O) => O.enterCallbacks = {}), y = Je(A, "beforeRouteEnter", p, _, We), y.push(k), se(y))).then(() => {
      y = [];
      for (const O of i.list())
        y.push(Z(O, p, _));
      return y.push(k), se(y);
    }).catch((O) => q(
      O,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? O : Promise.reject(O));
  }
  function bt(p, _, y) {
    u.list().forEach((E) => We(() => E(p, _, y)));
  }
  function Rt(p, _, y, E, V) {
    const A = R(p, _);
    if (A)
      return A;
    const k = _ === X, O = J ? history.state : {};
    y && (E || k ? o.replace(p.fullPath, C({
      scroll: k && O && O.scroll
    }, V)) : o.push(p.fullPath, V)), l.value = p, St(p, _, y, k), Fe();
  }
  let me;
  function Kn() {
    me || (me = o.listen((p, _, y) => {
      if (!Ot.listening)
        return;
      const E = w(p), V = U(E);
      if (V) {
        F(C(V, { replace: !0, force: !0 }), E).catch(we);
        return;
      }
      d = E;
      const A = l.value;
      J && No($t(A.fullPath, y.delta), je()), Et(E, A).catch((k) => q(
        k,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? k : q(
        k,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (F(
        C(b(k.to), {
          force: !0
        }),
        E
        // avoid an uncaught rejection, let push call triggerError
      ).then((O) => {
        q(
          O,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !y.delta && y.type === de.pop && o.go(-1, !1);
      }).catch(we), Promise.reject()) : (y.delta && o.go(-y.delta, !1), Le(k, E, A))).then((k) => {
        k = k || Rt(
          // after navigation, all matched components are resolved
          E,
          A,
          !1
        ), k && (y.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !q(
          k,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? o.go(-y.delta, !1) : y.type === de.pop && q(
          k,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && o.go(-1, !1)), bt(E, A, k);
      }).catch(we);
    }));
  }
  let Be = ye(), Pt = ye(), Se;
  function Le(p, _, y) {
    Fe(p);
    const E = Pt.list();
    return E.length ? E.forEach((V) => V(p, _, y)) : (P.NODE_ENV !== "production" && S("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function qn() {
    return Se && l.value !== X ? Promise.resolve() : new Promise((p, _) => {
      Be.add([p, _]);
    });
  }
  function Fe(p) {
    return Se || (Se = !p, Kn(), Be.list().forEach(([_, y]) => p ? y(p) : _()), Be.reset()), p;
  }
  function St(p, _, y, E) {
    const { scrollBehavior: V } = e;
    if (!J || !V)
      return Promise.resolve();
    const A = !y && Co($t(p.fullPath, 0)) || (E || !y) && history.state && history.state.scroll || null;
    return Ne().then(() => V(p, _, A)).then((k) => k && ko(k)).catch((k) => Le(k, p, _));
  }
  const Ue = (p) => o.go(p);
  let He;
  const Oe = /* @__PURE__ */ new Set(), Ot = {
    currentRoute: l,
    listening: !0,
    addRoute: h,
    removeRoute: g,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: m,
    resolve: w,
    options: e,
    push: N,
    replace: B,
    go: Ue,
    back: () => Ue(-1),
    forward: () => Ue(1),
    beforeEach: s.add,
    beforeResolve: i.add,
    afterEach: u.add,
    onError: Pt.add,
    isReady: qn,
    install(p) {
      const _ = this;
      p.component("RouterLink", as), p.component("RouterView", fs), p.config.globalProperties.$router = _, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => M(l)
      }), J && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !He && l.value === X && (He = !0, N(o.location).catch((V) => {
        P.NODE_ENV !== "production" && S("Unexpected error when starting the router:", V);
      }));
      const y = {};
      for (const V in X)
        Object.defineProperty(y, V, {
          get: () => l.value[V],
          enumerable: !0
        });
      p.provide(Me, _), p.provide(wt, Zn(y)), p.provide(ft, l);
      const E = p.unmount;
      Oe.add(p), p.unmount = function() {
        Oe.delete(p), Oe.size < 1 && (d = X, me && me(), me = null, l.value = X, He = !1, Se = !1), E();
      }, P.NODE_ENV !== "production" && J && ps(p, _, t);
    }
  };
  function se(p) {
    return p.reduce((_, y) => _.then(() => We(y)), Promise.resolve());
  }
  return Ot;
}
function Ss(e, t) {
  const n = [], r = [], o = [], s = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < s; i++) {
    const u = t.matched[i];
    u && (e.matched.find((d) => ee(d, u)) ? r.push(u) : n.push(u));
    const l = e.matched[i];
    l && (t.matched.find((d) => ee(d, l)) || o.push(l));
  }
  return [n, r, o];
}
function Os() {
  return K(Me);
}
function ks(e) {
  return K(wt);
}
function Ns(e) {
  const { immediately: t = !1, code: n } = e;
  let r = W(n);
  return t && (r = r()), r;
}
const Ee = /* @__PURE__ */ new Map();
function Cs(e) {
  if (!Ee.has(e)) {
    const t = Symbol();
    return Ee.set(e, t), t;
  }
  return Ee.get(e);
}
function ge(e, t) {
  var u, l;
  const n = Ge(e), r = Is(n, t);
  if (r.size > 0) {
    const d = Cs(e);
    le(d, r);
  }
  const o = oe({ attached: { varMap: r, sid: e } });
  jr({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: o,
    sid: e
  }), (u = n.js_watch) == null || u.forEach((d) => {
    qr(d, o);
  }), (l = n.vue_watch) == null || l.forEach((d) => {
    Kr(d, o);
  });
  function s(d, a) {
    const c = Ge(d);
    if (!c.vfor)
      return;
    const { fi: f } = c.vfor;
    f && (r.get(f.id).value = a.index);
  }
  function i(d) {
    const { sid: a, value: c } = d;
    if (!a)
      return;
    const f = Ge(a), { id: h } = f.sp, g = r.get(h);
    g.value = c;
  }
  return {
    updateVforInfo: s,
    updateSlotPropValue: i
  };
}
function oe(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, o, s] = As(n);
  t && r.set(t.sid, t.varMap);
  const i = o ? ks() : null, u = s ? Os() : null, l = o ? () => i : () => {
    throw new Error("Route params not found");
  }, d = s ? () => u : () => {
    throw new Error("Router not found");
  };
  function a(m) {
    const v = Ye(f(m));
    return ln(v, m.path ?? [], a);
  }
  function c(m) {
    const v = f(m);
    return br(v, {
      paths: m.path,
      getBindableValueFn: a
    });
  }
  function f(m) {
    return Vr(m) ? () => l()[m.prop] : r.get(m.sid).get(m.id);
  }
  function h(m, v) {
    if (vt(m)) {
      const w = f(m);
      if (m.path) {
        fn(w.value, m.path, v, a);
        return;
      }
      w.value = v;
      return;
    }
    throw new Error(`Unsupported output binding: ${m}`);
  }
  function g() {
    return d();
  }
  return {
    getValue: a,
    getRouter: g,
    getVueRefObject: c,
    updateValue: h,
    getVueRefObjectWithoutPath: f
  };
}
function Wn(e) {
  const t = Ee.get(e);
  return K(t);
}
function Vs(e) {
  const t = Wn(e);
  if (t === void 0)
    throw new Error(`Scope not found: ${e}`);
  return t;
}
function Is(e, t) {
  var o, s, i, u, l, d;
  const n = /* @__PURE__ */ new Map(), r = oe({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((a) => {
    n.set(a.id, a.value);
  }), e.jsFn && e.jsFn.forEach((a) => {
    const c = Ns(a);
    n.set(a.id, () => c);
  }), e.vfor && (t != null && t.initVforInfo)) {
    const { fv: a, fi: c, fk: f } = e.vfor, { index: h = 0, keyValue: g = null, config: m } = t.initVforInfo, { sid: v } = m, w = Qr(v);
    if (a) {
      const b = ue(() => ({
        get() {
          const R = w.value;
          return Array.isArray(R) ? R[h] : Object.values(R)[h];
        },
        set(R) {
          const N = w.value;
          if (!Array.isArray(N)) {
            N[g] = R;
            return;
          }
          N[h] = R;
        }
      }));
      n.set(a.id, b);
    }
    c && n.set(c.id, H(h)), f && n.set(f.id, H(g));
  }
  if (e.sp) {
    const { id: a } = e.sp, c = ((o = t == null ? void 0 : t.initSlotPropInfo) == null ? void 0 : o.value) || null;
    n.set(a, H(c));
  }
  return (s = e.eRefs) == null || s.forEach((a) => {
    n.set(a.id, H(null));
  }), (i = e.refs) == null || i.forEach((a) => {
    const c = Rr(a);
    n.set(a.id, c);
  }), (u = e.web_computed) == null || u.forEach((a) => {
    const c = Sr(a);
    n.set(a.id, c);
  }), (l = e.js_computed) == null || l.forEach((a) => {
    const c = Or(
      a,
      r
    );
    n.set(a.id, c);
  }), (d = e.vue_computed) == null || d.forEach((a) => {
    const c = Pr(
      a,
      r
    );
    n.set(a.id, c);
  }), n;
}
function As(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: o = !0 } = e;
    for (const s of n)
      t.set(s, Vs(s));
    return [t, r, o];
  }
  for (const n of Ee.keys()) {
    const r = Wn(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const $s = D(xs, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function xs(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = ge(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? pe(n[0]) : n.map((o) => pe(o)));
}
function qt(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let o = [];
  if (r > 0)
    for (let s = t; s < n; s += r)
      o.push(s);
  else
    for (let s = t; s > n; s += r)
      o.push(s);
  return o;
}
const Bn = D(Ts, {
  props: ["config"]
});
function Ts(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = oe(), s = Ms(t ?? "index"), i = Ws(e.config, r);
  return Jr(e.config, i), () => {
    const u = tr(i.value, (...l) => {
      const d = l[0], a = l[2] !== void 0, c = a ? l[2] : l[1], f = a ? l[1] : c, h = s(d, c);
      return $($s, {
        key: h,
        vforIndex: c,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? $(en, n, {
      default: () => u
    }) : u;
  };
}
const Ds = (e) => e, js = (e, t) => t;
function Ms(e) {
  const t = yr(e);
  return typeof t == "function" ? t : e === "item" ? Ds : js;
}
function Ws(e, t) {
  const { type: n, value: r } = e.array, o = n === ot.range;
  if (n === ot.const || o && typeof r == "number") {
    const i = o ? qt({
      end: Math.max(0, r)
    }) : r;
    return ue(() => ({
      get() {
        return i;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (o) {
    const i = r, u = t.getVueRefObject(i);
    return ue(() => ({
      get() {
        return qt({
          end: Math.max(0, u.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return ue(() => {
    const i = t.getVueRefObject(
      r
    );
    return {
      get() {
        return i.value;
      },
      set(u) {
        i.value = u;
      }
    };
  });
}
const Ln = D(Bs, {
  props: ["config"]
});
function Bs(e) {
  const { sid: t, items: n, on: r } = e.config;
  Pe(t) && ge(t);
  const o = oe();
  return () => (typeof r == "boolean" ? r : o.getValue(r)) ? n.map((i) => pe(i)) : void 0;
}
const Jt = D(Ls, {
  props: ["slotConfig"]
});
function Ls(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Pe(t) && ge(t), () => n.map((r) => pe(r));
}
const Qe = ":default", Fn = D(Fs, {
  props: ["config"]
});
function Fs(e) {
  const { on: t, caseValues: n, slots: r, sid: o } = e.config;
  Pe(o) && ge(o);
  const s = oe();
  return () => {
    const i = s.getValue(t), u = n.map((l, d) => {
      const a = d.toString(), c = r[a];
      return l === i ? $(Jt, { slotConfig: c, key: a }) : null;
    }).filter(Boolean);
    return u.length === 0 && Qe in r ? $(Jt, {
      slotConfig: r[Qe],
      key: Qe
    }) : u;
  };
}
const Us = "on:mounted";
function Hs(e, t, n) {
  if (!t)
    return e;
  const r = yt(() => []);
  t.map(([u, l]) => {
    const d = Gs(l, n), { eventName: a, handleEvent: c } = Qs({
      eventName: u,
      info: l,
      handleEvent: d
    });
    r.getOrDefault(a).push(c);
  });
  const o = {};
  for (const [u, l] of r) {
    const d = l.length === 1 ? l[0] : (...a) => l.forEach((c) => Promise.resolve().then(() => c(...a)));
    o[u] = d;
  }
  const { [Us]: s, ...i } = o;
  return e = Ce(e, i), s && (e = tn(e, [
    [
      {
        mounted(u) {
          s(u);
        }
      }
    ]
  ])), e;
}
function Gs(e, t) {
  if (e.type === "web") {
    const n = zs(e, t);
    return Ks(e, n, t);
  } else {
    if (e.type === "vue")
      return Js(e, t);
    if (e.type === "js")
      return qs(e, t);
  }
  throw new Error(`unknown event type ${e}`);
}
function zs(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: o, type: s }) => {
    if (s === G.EventContext) {
      const { path: i } = o;
      if (i.startsWith(":")) {
        const u = i.slice(1);
        return W(u)(...r);
      }
      return Gr(r[0], i.split("."));
    }
    return s === G.Ref ? t.getValue(o) : o;
  });
}
function Ks(e, t, n) {
  async function r(...o) {
    const s = t(...o), i = pn({
      config: e.preSetup,
      varGetter: n
    });
    try {
      i.run();
      const u = await hn().eventSend(e, s);
      if (!u)
        return;
      Te(u, e.sets, n);
    } finally {
      i.tryReset();
    }
  }
  return r;
}
function qs(e, t) {
  const { sets: n, code: r, inputs: o = [] } = e, s = W(r);
  function i(...u) {
    const l = o.map(({ value: a, type: c }) => {
      if (c === G.EventContext) {
        if (a.path.startsWith(":")) {
          const f = a.path.slice(1);
          return W(f)(...u);
        }
        return Hr(u[0], a.path.split("."));
      }
      if (c === G.Ref)
        return mn(t.getValue(a));
      if (c === G.Data)
        return a;
      if (c === G.JsFn)
        return t.getValue(a);
      throw new Error(`unknown input type ${c}`);
    }), d = s(...l);
    if (n !== void 0) {
      const c = n.length === 1 ? [d] : d, f = c.map((h) => h === void 0 ? 1 : 0);
      Te(
        { values: c, types: f },
        n,
        t
      );
    }
  }
  return i;
}
function Js(e, t) {
  const { code: n, inputs: r = {} } = e, o = De(
    r,
    (u) => u.type !== G.Data ? t.getVueRefObject(u.value) : u.value
  ), s = W(n, o);
  function i(...u) {
    s(...u);
  }
  return i;
}
function Qs(e) {
  const { eventName: t, info: n, handleEvent: r } = e;
  if (n.type === "vue")
    return {
      eventName: t,
      handleEvent: r
    };
  const { modifier: o = [] } = n;
  if (o.length === 0)
    return {
      eventName: t,
      handleEvent: r
    };
  const s = ["passive", "capture", "once"], i = [], u = [];
  for (const a of o)
    s.includes(a) ? i.push(a[0].toUpperCase() + a.slice(1)) : u.push(a);
  const l = i.length > 0 ? t + i.join("") : t, d = u.length > 0 ? nr(r, u) : r;
  return {
    eventName: l,
    handleEvent: d
  };
}
function Ys(e, t) {
  const n = [];
  (e.bStyle || []).forEach((s) => {
    Array.isArray(s) ? n.push(
      ...s.map((i) => t.getValue(i))
    ) : n.push(
      De(
        s,
        (i) => t.getValue(i)
      )
    );
  });
  const r = rr([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function Xs(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return Ve(n);
  const { str: r, map: o, bind: s } = n, i = [];
  return r && i.push(r), o && i.push(
    De(
      o,
      (u) => t.getValue(u)
    )
  ), s && i.push(...s.map((u) => t.getValue(u))), Ve(i);
}
function $e(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => $e(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (o) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            o
          );
        }
      else
        t && $e(r, !0);
  }
}
function Zs(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = W(t)), { name: e, value: t, isFunc: n };
}
function ei(e, t, n) {
  var o;
  const r = {};
  return Nt(e.bProps || {}, (s, i) => {
    const u = n.getValue(s);
    Re(u) || ($e(u), r[i] = ti(u, i));
  }), (o = e.proxyProps) == null || o.forEach((s) => {
    const i = n.getValue(s);
    typeof i == "object" && Nt(i, (u, l) => {
      const { name: d, value: a } = Zs(l, u);
      r[d] = a;
    });
  }), { ...t, ...r };
}
function ti(e, t) {
  return t === "innerText" ? xe(e) : e;
}
const ni = D(ri, {
  props: ["slotPropValue", "config"]
});
function ri(e) {
  const { sid: t, items: n } = e.config, r = Pe(t) ? ge(t, {
    initSlotPropInfo: {
      value: e.slotPropValue
    }
  }).updateSlotPropValue : oi;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((o) => pe(o)));
}
function oi() {
}
function si(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? ht(n[":"]) : gn(n, { keyFn: (i) => i === ":" ? "default" : i, valueFn: (i) => (u) => i.use_prop ? ii(u, i) : ht(i) });
}
function ii(e, t) {
  return $(ni, { config: t, slotPropValue: e });
}
function ai(e, t, n) {
  const r = [], { dir: o = [] } = t;
  return o.forEach((s) => {
    const { sys: i, name: u, arg: l, value: d, mf: a } = s;
    if (u === "vmodel") {
      const c = n.getVueRefObject(d);
      if (e = Ce(e, {
        [`onUpdate:${l}`]: (f) => {
          c.value = f;
        }
      }), i === 1) {
        const f = a ? Object.fromEntries(a.map((h) => [h, !0])) : {};
        r.push([or, c.value, void 0, f]);
      } else
        e = Ce(e, {
          [l]: c.value
        });
    } else if (u === "vshow") {
      const c = n.getVueRefObject(d);
      r.push([sr, c.value]);
    } else
      console.warn(`Directive ${u} is not supported yet`);
  }), tn(e, r);
}
function ci(e, t, n) {
  const { eRef: r } = t;
  return r ? Ce(e, { ref: n.getVueRefObject(r) }) : e;
}
const Un = Symbol();
function ui(e) {
  le(Un, e);
}
function Li() {
  return K(Un);
}
const li = D(fi, {
  props: ["config"]
});
function fi(e) {
  const { config: t } = e, n = oe({
    sidCollector: new di(t).getCollectInfo()
  });
  t.varGetterStrategy && ui(n);
  const r = t.props ?? {};
  return $e(r, !0), () => {
    const { tag: o } = t, s = typeof o == "string" ? o : n.getValue(o), i = ir(s), u = typeof i == "string", l = Xs(t, n), { styles: d, hasStyle: a } = Ys(t, n), c = si(t, u), f = ei(t, r, n), h = ar(f) || {};
    a && (h.style = d), l && (h.class = l);
    let g = $(i, { ...h }, c);
    return g = Hs(g, t.events, n), g = ci(g, t, n), ai(g, t, n);
  };
}
class di {
  constructor(t) {
    x(this, "sids", /* @__PURE__ */ new Set());
    x(this, "needRouteParams", !0);
    x(this, "needRouter", !0);
    this.config = t;
  }
  /**
   * getCollectFn
   */
  getCollectInfo() {
    const {
      eRef: t,
      dir: n,
      classes: r,
      bProps: o,
      proxyProps: s,
      bStyle: i,
      events: u,
      varGetterStrategy: l
    } = this.config;
    if (l !== "all") {
      if (t && this._tryExtractSidToCollection(t), n && n.forEach((d) => {
        this._tryExtractSidToCollection(d.value), this._extendWithPaths(d.value);
      }), r && typeof r != "string") {
        const { map: d, bind: a } = r;
        d && Object.values(d).forEach((c) => {
          this._tryExtractSidToCollection(c), this._extendWithPaths(c);
        }), a && a.forEach((c) => {
          this._tryExtractSidToCollection(c), this._extendWithPaths(c);
        });
      }
      return o && Object.values(o).forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), s && s.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), i && i.forEach((d) => {
        Array.isArray(d) ? d.forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        }) : Object.values(d).forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        });
      }), u && u.forEach(([d, a]) => {
        this._handleEventInputs(a), this._handleEventSets(a);
      }), Array.isArray(l) && l.forEach((d) => {
        this.sids.add(d.sid);
      }), {
        sids: this.sids,
        needRouteParams: this.needRouteParams,
        needRouter: this.needRouter
      };
    }
  }
  _tryExtractSidToCollection(t) {
    dn(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    if (t.type === "js" || t.type === "web") {
      const { inputs: n } = t;
      n == null || n.forEach((r) => {
        if (r.type === G.Ref) {
          const o = r.value;
          this._tryExtractSidToCollection(o), this._extendWithPaths(o);
        }
      });
    } else if (t.type === "vue") {
      const { inputs: n } = t;
      if (n) {
        const r = Object.values(n);
        r == null || r.forEach((o) => {
          if (o.type === G.Ref) {
            const s = o.value;
            this._tryExtractSidToCollection(s), this._extendWithPaths(s);
          }
        });
      }
    }
  }
  _handleEventSets(t) {
    if (t.type === "js" || t.type === "web") {
      const { sets: n } = t;
      n == null || n.forEach((r) => {
        vt(r.ref) && (this.sids.add(r.ref.sid), this._extendWithPaths(r.ref));
      });
    }
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (wr(r)) {
        const o = Er(r);
        this._tryExtractSidToCollection(o), o.path && n.push(...o.path);
      }
    }
  }
}
function pe(e, t) {
  return kr(e) ? $(Bn, { config: e, key: t }) : Nr(e) ? $(Ln, { config: e, key: t }) : Cr(e) ? $(Fn, { config: e, key: t }) : $(li, { config: e, key: t });
}
function ht(e, t) {
  return $(Hn, { slotConfig: e, key: t });
}
const Hn = D(hi, {
  props: ["slotConfig"]
});
function hi(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Pe(t) && ge(t), () => n.map((r) => pe(r));
}
function pi(e, t) {
  const { state: n, isReady: r, isLoading: o } = vr(async () => {
    let s = e;
    const i = t;
    if (!s && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!s && i && (s = await (await fetch(i)).json()), !s)
      throw new Error("Failed to load config");
    return s;
  }, {});
  return { config: n, isReady: r, isLoading: o };
}
function gi(e) {
  const t = Y(!1), n = Y("");
  function r(o, s) {
    let i;
    return s.component ? i = `Error captured from component:tag: ${s.component.tag} ; id: ${s.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", s.component), console.error("Error:", o), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${o.message}`), !1;
  }
  return cr(r), { hasError: t, errorMessage: n };
}
let pt;
function mi(e) {
  if (e === "web" || e === "webview") {
    pt = vi;
    return;
  }
  if (e === "zero") {
    pt = yi;
    return;
  }
  throw new Error(`Unsupported mode: ${e}`);
}
function vi(e) {
  const { assetPath: t = "/assets/icons", icon: n = "" } = e, [r, o] = n.split(":");
  return {
    assetPath: t,
    svgName: `${r}.svg`
  };
}
function yi() {
  return {
    assetPath: "",
    svgName: ""
  };
}
function _i(e, t) {
  const n = T(() => {
    const i = e.value;
    if (!i)
      return null;
    const d = new DOMParser().parseFromString(i, "image/svg+xml").querySelector("svg");
    if (!d)
      throw new Error("Invalid svg string");
    const a = {};
    for (const f of d.attributes)
      a[f.name] = f.value;
    const c = d.innerHTML;
    return {
      ...a,
      innerHTML: c
    };
  }), { size: r, color: o } = t, s = T(() => {
    const i = {};
    return r.value !== null && r.value !== void 0 && (i.width = r.value.toString(), i.height = r.value.toString()), o.value !== null && o.value !== void 0 && (i.fill = o.value), {
      ...n.value,
      ...i
    };
  });
  return () => {
    if (!n.value)
      return null;
    const i = s.value;
    return $("svg", i);
  };
}
const wi = {
  class: "app-box insta-themes",
  "data-scaling": "100%"
}, Ei = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, bi = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, Ri = /* @__PURE__ */ D({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: o } = pi(
      t.config,
      t.configUrl
    );
    z(r, (u) => {
      u.url && (hr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: u.url.path,
        pathParams: u.url.params,
        webServerInfo: u.webInfo
      }), xr(t.meta.mode)), mi(t.meta.mode), pr(u);
    });
    const { hasError: s, errorMessage: i } = gi(n);
    return (u, l) => (Q(), ne("div", wi, [
      M(o) ? (Q(), ne("div", Ei, l[0] || (l[0] = [
        nn("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (Q(), ne("div", {
        key: 1,
        class: Ve(["insta-main", M(r).class])
      }, [
        ur(M(Hn), { "slot-config": M(r) }, null, 8, ["slot-config"]),
        M(s) ? (Q(), ne("div", bi, xe(M(i)), 1)) : Xe("", !0)
      ], 2))
    ]));
  }
});
function Pi(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => $(
    en,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const Si = D(Pi, {
  props: ["name", "tag"]
});
function Oi(e) {
  const { content: t, r: n = 0 } = e, r = oe(), o = n === 1 ? () => r.getValue(t) : () => t;
  return () => xe(o());
}
const ki = D(Oi, {
  props: ["content", "r"]
});
function Ni(e) {
  return `i-size-${e}`;
}
function Ci(e) {
  return e ? `i-weight-${e}` : "";
}
function Vi(e) {
  return e ? `i-text-align-${e}` : "";
}
const Ii = /* @__PURE__ */ D({
  __name: "Heading",
  props: {
    text: {},
    size: {},
    weight: {},
    align: {}
  },
  setup(e) {
    const t = e, n = T(() => [
      Ni(t.size ?? "6"),
      Ci(t.weight),
      Vi(t.align)
    ]);
    return (r, o) => (Q(), ne("h1", {
      class: Ve(["insta-Heading", n.value])
    }, xe(r.text), 3));
  }
}), Ai = /* @__PURE__ */ D({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (Q(), rn(lr, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      fr(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), $i = ["width", "height", "fill"], xi = ["xlink:href"], Ti = /* @__PURE__ */ D({
  __name: "Icon",
  props: {
    size: {},
    icon: {},
    color: {},
    assetPath: {},
    svgName: {},
    rawSvg: {}
  },
  setup(e) {
    const t = e, { assetPath: n, svgName: r } = pt(t), o = ie(() => t.icon ? t.icon.split(":")[1] : ""), s = ie(() => t.size || "1em"), i = ie(() => t.color || "currentColor"), u = ie(() => t.rawSvg || null), l = T(() => `${n}/${r}/#${o.value}`), d = _i(u, {
      size: ie(() => t.size),
      color: ie(() => t.color)
    });
    return (a, c) => (Q(), ne(on, null, [
      o.value ? (Q(), ne("svg", {
        key: 0,
        width: s.value,
        height: s.value,
        fill: i.value
      }, [
        nn("use", { "xlink:href": l.value }, null, 8, xi)
      ], 8, $i)) : Xe("", !0),
      u.value ? (Q(), rn(M(d), { key: 1 })) : Xe("", !0)
    ], 64));
  }
});
function Di(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t, kAlive: n = !1 } = e.router;
  return t.map(
    (o) => Gn(o, n)
  );
}
function Gn(e, t) {
  var u;
  const { server: n = !1, vueItem: r } = e, o = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(ji(e, t));
  }, s = (u = r.children) == null ? void 0 : u.map(
    (l) => Gn(l, t)
  ), i = {
    ...r,
    children: s,
    component: o
  };
  return r.component.length === 0 && delete i.component, s === void 0 && delete i.children, i;
}
function ji(e, t) {
  const { sid: n, vueItem: r } = e, { path: o, component: s } = r, i = ht(
    {
      items: s,
      sid: n
    },
    o
  ), u = $(on, null, i);
  return t ? $(dr, null, () => i) : u;
}
function Mi(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? xo() : n === "memory" ? $o() : Nn();
  e.use(
    Ps({
      history: r,
      routes: Di(t)
    })
  );
}
function Fi(e, t) {
  e.component("insta-ui", Ri), e.component("vif", Ln), e.component("vfor", Bn), e.component("match", Fn), e.component("teleport", Ai), e.component("icon", Ti), e.component("ts-group", Si), e.component("content", ki), e.component("heading", Ii), t.router && Mi(e, t);
}
export {
  $e as convertDynamicProperties,
  Fi as install,
  Li as useVarGetter
};
//# sourceMappingURL=insta-ui.js.map
