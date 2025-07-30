var Qn = Object.defineProperty;
var Jn = (e, t, n) => t in e ? Qn(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var x = (e, t, n) => Jn(e, typeof t != "symbol" ? t + "" : t, n);
import * as Yn from "vue";
import { unref as M, watch as z, nextTick as Ne, isRef as Qt, ref as Y, shallowRef as H, watchEffect as Jt, computed as T, toRaw as Yt, customRef as ce, toValue as Ye, readonly as Xn, provide as ue, inject as K, shallowReactive as Zn, defineComponent as D, reactive as er, h as A, getCurrentInstance as Xt, renderList as tr, TransitionGroup as Zt, cloneVNode as Ve, withDirectives as en, normalizeStyle as nr, normalizeClass as Ce, toDisplayString as xe, vModelDynamic as rr, vShow as or, resolveDynamicComponent as sr, normalizeProps as ir, onErrorCaptured as ar, openBlock as J, createElementBlock as ne, createElementVNode as tn, createVNode as cr, createCommentVNode as Xe, createBlock as nn, Teleport as ur, renderSlot as lr, toRef as ie, Fragment as rn, KeepAlive as fr } from "vue";
let on;
function dr(e) {
  on = e;
}
function Ze() {
  return on;
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
function hr(e) {
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
function me(e) {
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
      tt(g, m).then(() => me(e)).finally(() => v == null ? void 0 : v())
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
        ([W, U]) => {
          t !== (W === U) && (w ? w() : Ne(() => w == null ? void 0 : w()), N(W));
        },
        {
          flush: h,
          deep: g,
          immediate: !0
        }
      );
    })];
    return m != null && R.push(
      tt(m, v).then(() => me(e)).finally(() => (w == null || w(), me(e)))
    ), Promise.race(R);
  }
  function o(c) {
    return n((f) => !!f, c);
  }
  function i(c) {
    return r(null, c);
  }
  function s(c) {
    return r(void 0, c);
  }
  function u(c) {
    return n(Number.isNaN, c);
  }
  function l(c, f) {
    return n((h) => {
      const g = Array.from(h);
      return g.includes(c) || g.includes(me(c));
    }, f);
  }
  function d(c) {
    return a(1, c);
  }
  function a(c = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= c), f);
  }
  return Array.isArray(me(e)) ? {
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
    toBeNull: i,
    toBeNaN: u,
    toBeUndefined: s,
    changed: d,
    changedTimes: a,
    get not() {
      return nt(e, !t);
    }
  };
}
function pr(e) {
  return nt(e);
}
function gr(e, t, n) {
  let r;
  Qt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: o = !1,
    evaluating: i = void 0,
    shallow: s = !0,
    onError: u = et
  } = r, l = Y(!o), d = s ? H(t) : Y(t);
  let a = 0;
  return Jt(async (c) => {
    if (!l.value)
      return;
    a++;
    const f = a;
    let h = !1;
    i && Promise.resolve().then(() => {
      i.value = !0;
    });
    try {
      const g = await e((m) => {
        c(() => {
          i && (i.value = !1), h || m();
        });
      });
      f === a && (d.value = g);
    } catch (g) {
      u(g);
    } finally {
      i && f === a && (i.value = !1), h = !0;
    }
  }), o ? T(() => (l.value = !0, d.value)) : d;
}
function mr(e, t, n) {
  const {
    immediate: r = !0,
    delay: o = 0,
    onError: i = et,
    onSuccess: s = et,
    resetOnExecute: u = !0,
    shallow: l = !0,
    throwError: d
  } = {}, a = l ? H(t) : Y(t), c = Y(!1), f = Y(!1), h = H(void 0);
  async function g(w = 0, ...b) {
    u && (a.value = t), h.value = void 0, c.value = !1, f.value = !0, w > 0 && await tt(w);
    const R = typeof e == "function" ? e(...b) : e;
    try {
      const N = await R;
      a.value = N, c.value = !0, s(N);
    } catch (N) {
      if (h.value = N, i(N), d)
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
      pr(f).toBe(!1).then(() => w(m)).catch(b);
    });
  }
  return {
    ...m,
    then(w, b) {
      return v().then(w, b);
    }
  };
}
function B(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Yn];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (o) {
    throw new Error(o + " in function code: " + e);
  }
}
function vr(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return B(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function sn(e) {
  return e.constructor.name === "AsyncFunction";
}
class yr {
  toString() {
    return "";
  }
}
const be = new yr();
function Re(e) {
  return Yt(e) === be;
}
function _r(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function wr(e) {
  return e[1];
}
function an(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...i] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + i[0];
      case "~+":
        return i[0] + e;
    }
  }
  const r = cn(t, n);
  return e[r];
}
function cn(e, t) {
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
function un(e, t, n) {
  return t.reduce(
    (r, o) => an(r, o, n),
    e
  );
}
function ln(e, t, n, r) {
  t.reduce((o, i, s) => {
    if (s === t.length - 1)
      o[cn(i, r)] = n;
    else
      return an(o, i, r);
  }, e);
}
function Er(e, t, n) {
  const { paths: r, getBindableValueFn: o } = t, { paths: i, getBindableValueFn: s } = t;
  return r === void 0 || r.length === 0 ? e : ce(() => ({
    get() {
      try {
        return un(
          Ye(e),
          r,
          o
        );
      } catch {
        return;
      }
    },
    set(u) {
      ln(
        Ye(e),
        i || r,
        u,
        s
      );
    }
  }));
}
function mt(e) {
  return ce((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      !Re(e) && JSON.stringify(r) === JSON.stringify(e) || (e = r, n());
    }
  }));
}
function br(e, t) {
  const { deepCompare: n = !1 } = e;
  return n ? mt(e.value) : Y(e.value);
}
function Rr(e, t, n) {
  const { bind: r = {}, code: o, const: i = [] } = e, s = Object.values(r).map((a, c) => i[c] === 1 ? a : t.getVueRefObject(a));
  if (sn(new Function(o)))
    return gr(
      async () => {
        const a = Object.fromEntries(
          Object.keys(r).map((c, f) => [c, s[f]])
        );
        return await B(o, a)();
      },
      null,
      { lazy: !0 }
    );
  const u = Object.fromEntries(
    Object.keys(r).map((a, c) => [a, s[c]])
  ), l = B(o, u);
  return T(l);
}
function Pr(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? H(t ?? be) : mt(t ?? be);
}
function Sr(e, t, n) {
  const {
    inputs: r = [],
    code: o,
    slient: i,
    data: s,
    asyncInit: u = null,
    deepEqOnInput: l = 0
  } = e, d = i || Array(r.length).fill(0), a = s || Array(r.length).fill(0), c = r.filter((v, w) => d[w] === 0 && a[w] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map(
      (v, w) => a[w] === 1 ? v : t.getValue(v)
    );
  }
  const h = B(o), g = l === 0 ? H(be) : mt(be), m = { immediate: !0, deep: !0 };
  return sn(h) ? (g.value = u, z(
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
function Or(e) {
  return e.tag === "vfor";
}
function kr(e) {
  return e.tag === "vif";
}
function Nr(e) {
  return e.tag === "match";
}
function fn(e) {
  return !("type" in e);
}
function Vr(e) {
  return "type" in e && e.type === "rp";
}
function vt(e) {
  return "sid" in e && "id" in e;
}
class Cr extends Map {
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
function dn(e) {
  return new Cr(e);
}
class Ir {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: i } = t, s = Ze().webServerInfo, u = i !== void 0 ? { key: i } : {}, l = r === "sync" ? s.event_url : s.event_async_url;
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
    const { fType: n, key: r } = t.watchConfig, o = Ze().webServerInfo, i = n === "sync" ? o.watch_url : o.watch_async_url, s = t.getServerInputs(), u = {
      key: r,
      input: s,
      page: Ie()
    };
    return await (await fetch(i, {
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
    const { fType: r, hKey: o, key: i } = t, s = i !== void 0 ? { key: i } : {};
    let u = {};
    const l = {
      bind: n,
      fType: r,
      hKey: o,
      ...s,
      page: Ie(),
      ...u
    };
    return await window.pywebview.api.event_call(l);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = t.getServerInputs(), i = {
      key: r,
      input: o,
      fType: n,
      page: Ie()
    };
    return await window.pywebview.api.watch_call(i);
  }
}
let rt;
function Ar(e) {
  switch (e) {
    case "web":
      rt = new Ir();
      break;
    case "webview":
      rt = new $r();
      break;
  }
}
function hn() {
  return rt;
}
var G = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(G || {}), ot = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(ot || {}), _e = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e))(_e || {});
function xr(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: _e.Ref
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
  const r = t.map((s) => {
    const u = n.getVueRefObject(s.target);
    return s.type === "const" ? {
      refObj: u,
      preValue: u.value,
      newValue: s.value,
      reset: !0
    } : Tr(u, s, n);
  });
  return {
    run: () => {
      r.forEach((s) => {
        s.newValue !== s.preValue && (s.refObj.value = s.newValue);
      });
    },
    tryReset: () => {
      r.forEach((s) => {
        s.reset && (s.refObj.value = s.preValue);
      });
    }
  };
}
function Tr(e, t, n) {
  const r = B(t.code), o = t.inputs.map((i) => n.getValue(i));
  return {
    refObj: e,
    preValue: e.value,
    reset: t.reset ?? !0,
    newValue: r(...o)
  };
}
function Ot(e) {
  return e == null;
}
function Te(e, t, n) {
  if (Ot(t) || Ot(e.values))
    return;
  t = t;
  const r = e.values, o = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((i, s) => {
    const u = o[s];
    if (u === 1)
      return;
    if (i.type === _e.Ref) {
      if (u === 2) {
        r[s].forEach(([a, c]) => {
          const f = i.ref, h = {
            ...f,
            path: [...f.path ?? [], ...a]
          };
          n.updateValue(h, c);
        });
        return;
      }
      n.updateValue(i.ref, r[s]);
      return;
    }
    if (i.type === _e.RouterAction) {
      const d = r[s], a = n.getRouter()[d.fn];
      a(...d.args);
      return;
    }
    if (i.type === _e.ElementRefAction) {
      const d = i.ref, a = n.getVueRefObject(d).value, c = r[s], { method: f, args: h = [] } = c;
      a[f](...h);
      return;
    }
    const l = n.getVueRefObject(
      i.ref
    );
    l.value = r[s];
  });
}
function Dr(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: o } = e;
  return new jr(t, n, r, o);
}
class jr {
  constructor(t, n, r, o) {
    x(this, "taskQueue", []);
    x(this, "id2TaskMap", /* @__PURE__ */ new Map());
    x(this, "input2TaskIdMap", dn(() => []));
    this.varMapGetter = r;
    const i = [], s = (u) => {
      var d;
      const l = new Mr(u, r);
      return this.id2TaskMap.set(l.id, l), (d = u.inputs) == null || d.forEach((a, c) => {
        var h, g;
        if (((h = u.data) == null ? void 0 : h[c]) === 0 && ((g = u.slient) == null ? void 0 : g[c]) === 0) {
          if (!fn(a))
            throw new Error("Non-var input bindings are not supported.");
          const m = `${a.sid}-${a.id}`;
          this.input2TaskIdMap.getOrDefault(m).push(l.id);
        }
      }), l;
    };
    t == null || t.forEach((u) => {
      const l = s(u);
      i.push(l);
    }), n == null || n.forEach((u) => {
      const l = s(
        xr(o, u)
      );
      i.push(l);
    }), i.forEach((u) => {
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
          g.some(Re) || (u.modify = !0, this.taskQueue.push(new Wr(u)), this._scheduleNextTick());
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
      (i, s) => !r[s] && !n[s]
    ).map((i) => this.varMapGetter.getVueRefObject(i));
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
      (i) => o.has(i.watchTask.id) && i.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!vt(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: o, id: i } = r.ref, s = `${o}-${i}`;
      (this.input2TaskIdMap.get(s) || []).forEach((l) => n.add(l));
    }), n;
  }
}
class Mr {
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
class Wr {
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
        await Br(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function Br(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, o = pn({
    config: r,
    varGetter: t
  });
  try {
    o.run(), e.taskDone();
    const i = await hn().watchSend(e);
    if (!i)
      return;
    Te(i, n, t);
  } finally {
    o.tryReset();
  }
}
function kt(e, t) {
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
    Object.entries(e).map(([o, i], s) => [
      r ? r(o, i) : o,
      n(i, o, s)
    ])
  );
}
function Lr(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...i] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + i[0];
      case "~+":
        return i[0] + e;
    }
  }
  const r = Fr(t);
  return e[r];
}
function Fr(e, t) {
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
function Ur(e, t, n) {
  return t.reduce(
    (r, o) => Lr(r, o),
    e
  );
}
function Hr(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Gr = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function mn(e) {
  return typeof e == "function" ? e : Gr(Yt(e));
}
function zr(e, t) {
  const {
    on: n,
    code: r,
    immediate: o,
    deep: i,
    once: s,
    flush: u,
    bind: l = {},
    onData: d,
    bindData: a
  } = e, c = d || Array.from({ length: n.length }).fill(0), f = a || Array.from({ length: Object.keys(l).length }).fill(0), h = De(
    l,
    (v, w, b) => f[b] === 0 ? t.getVueRefObject(v) : v
  ), g = B(r, h), m = n.length === 1 ? Nt(c[0] === 1, n[0], t) : n.map(
    (v, w) => Nt(c[w] === 1, v, t)
  );
  return z(m, g, { immediate: o, deep: i, once: s, flush: u });
}
function Nt(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function Kr(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: o,
    data: i,
    code: s,
    immediate: u = !0,
    deep: l,
    once: d,
    flush: a
  } = e, c = o || Array.from({ length: n.length }).fill(0), f = i || Array.from({ length: n.length }).fill(0), h = B(s), g = n.filter((v, w) => c[w] === 0 && f[w] === 0).map((v) => t.getVueRefObject(v));
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
const st = dn(() => Symbol());
function qr(e, t) {
  const n = e.sid, r = st.getOrDefault(n);
  st.set(n, r), ue(r, t);
}
function Qr(e) {
  const t = st.get(e);
  return K(t);
}
function Jr() {
  return vn().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function vn() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const Yr = typeof Proxy == "function", Xr = "devtools-plugin:setup", Zr = "plugin:settings:set";
let ae, it;
function eo() {
  var e;
  return ae !== void 0 || (typeof window < "u" && window.performance ? (ae = !0, it = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (ae = !0, it = globalThis.perf_hooks.performance) : ae = !1), ae;
}
function to() {
  return eo() ? it.now() : Date.now();
}
class no {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const s in t.settings) {
        const u = t.settings[s];
        r[s] = u.defaultValue;
      }
    const o = `__vue-devtools-plugin-settings__${t.id}`;
    let i = Object.assign({}, r);
    try {
      const s = localStorage.getItem(o), u = JSON.parse(s);
      Object.assign(i, u);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return i;
      },
      setSettings(s) {
        try {
          localStorage.setItem(o, JSON.stringify(s));
        } catch {
        }
        i = s;
      },
      now() {
        return to();
      }
    }, n && n.on(Zr, (s, u) => {
      s === this.plugin.id && this.fallbacks.setSettings(u);
    }), this.proxiedOn = new Proxy({}, {
      get: (s, u) => this.target ? this.target.on[u] : (...l) => {
        this.onQueue.push({
          method: u,
          args: l
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (s, u) => this.target ? this.target[u] : u === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(u) ? (...l) => (this.targetQueue.push({
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
function ro(e, t) {
  const n = e, r = vn(), o = Jr(), i = Yr && n.enableEarlyProxy;
  if (o && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !i))
    o.emit(Xr, e, t);
  else {
    const s = i ? new no(n, o) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: s
    }), s && t(s.proxiedTarget);
  }
}
var P = {};
const Q = typeof document < "u";
function yn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function oo(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && yn(e.default);
}
const V = Object.assign;
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
const _n = /#/g, so = /&/g, io = /\//g, ao = /=/g, co = /\?/g, wn = /\+/g, uo = /%5B/g, lo = /%5D/g, En = /%5E/g, fo = /%60/g, bn = /%7B/g, ho = /%7C/g, Rn = /%7D/g, po = /%20/g;
function yt(e) {
  return encodeURI("" + e).replace(ho, "|").replace(uo, "[").replace(lo, "]");
}
function go(e) {
  return yt(e).replace(bn, "{").replace(Rn, "}").replace(En, "^");
}
function at(e) {
  return yt(e).replace(wn, "%2B").replace(po, "+").replace(_n, "%23").replace(so, "%26").replace(fo, "`").replace(bn, "{").replace(Rn, "}").replace(En, "^");
}
function mo(e) {
  return at(e).replace(ao, "%3D");
}
function vo(e) {
  return yt(e).replace(_n, "%23").replace(co, "%3F");
}
function yo(e) {
  return e == null ? "" : vo(e).replace(io, "%2F");
}
function le(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    P.NODE_ENV !== "production" && S(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const _o = /\/$/, wo = (e) => e.replace(_o, "");
function Ke(e, t, n = "/") {
  let r, o = {}, i = "", s = "";
  const u = t.indexOf("#");
  let l = t.indexOf("?");
  return u < l && u >= 0 && (l = -1), l > -1 && (r = t.slice(0, l), i = t.slice(l + 1, u > -1 ? u : t.length), o = e(i)), u > -1 && (r = r || t.slice(0, u), s = t.slice(u, t.length)), r = Ro(r ?? t, n), {
    fullPath: r + (i && "?") + i + s,
    path: r,
    query: o,
    hash: le(s)
  };
}
function Eo(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Vt(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function Ct(e, t, n) {
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
    if (!bo(e[n], t[n]))
      return !1;
  return !0;
}
function bo(e, t) {
  return L(e) ? It(e, t) : L(t) ? It(t, e) : e === t;
}
function It(e, t) {
  return L(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function Ro(e, t) {
  if (e.startsWith("/"))
    return e;
  if (P.NODE_ENV !== "production" && !t.startsWith("/"))
    return S(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), o = r[r.length - 1];
  (o === ".." || o === ".") && r.push("");
  let i = n.length - 1, s, u;
  for (s = 0; s < r.length; s++)
    if (u = r[s], u !== ".")
      if (u === "..")
        i > 1 && i--;
      else
        break;
  return n.slice(0, i).join("/") + "/" + r.slice(s).join("/");
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
var fe;
(function(e) {
  e.pop = "pop", e.push = "push";
})(fe || (fe = {}));
var re;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(re || (re = {}));
const qe = "";
function Sn(e) {
  if (!e)
    if (Q) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), wo(e);
}
const Po = /^[^#]+#/;
function On(e, t) {
  return e.replace(Po, "#") + t;
}
function So(e, t) {
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
function Oo(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (P.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const i = document.querySelector(e.el);
        if (r && i) {
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
    t = So(o, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function $t(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const ct = /* @__PURE__ */ new Map();
function ko(e, t) {
  ct.set(e, t);
}
function No(e) {
  const t = ct.get(e);
  return ct.delete(e), t;
}
let Vo = () => location.protocol + "//" + location.host;
function kn(e, t) {
  const { pathname: n, search: r, hash: o } = t, i = e.indexOf("#");
  if (i > -1) {
    let u = o.includes(e.slice(i)) ? e.slice(i).length : 1, l = o.slice(u);
    return l[0] !== "/" && (l = "/" + l), Vt(l, "");
  }
  return Vt(n, e) + r + o;
}
function Co(e, t, n, r) {
  let o = [], i = [], s = null;
  const u = ({ state: f }) => {
    const h = kn(e, location), g = n.value, m = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, s && s === g) {
        s = null;
        return;
      }
      v = m ? f.position - m.position : 0;
    } else
      r(h);
    o.forEach((w) => {
      w(n.value, g, {
        delta: v,
        type: fe.pop,
        direction: v ? v > 0 ? re.forward : re.back : re.unknown
      });
    });
  };
  function l() {
    s = n.value;
  }
  function d(f) {
    o.push(f);
    const h = () => {
      const g = o.indexOf(f);
      g > -1 && o.splice(g, 1);
    };
    return i.push(h), h;
  }
  function a() {
    const { history: f } = window;
    f.state && f.replaceState(V({}, f.state, { scroll: je() }), "");
  }
  function c() {
    for (const f of i)
      f();
    i = [], window.removeEventListener("popstate", u), window.removeEventListener("beforeunload", a);
  }
  return window.addEventListener("popstate", u), window.addEventListener("beforeunload", a, {
    passive: !0
  }), {
    pauseListeners: l,
    listen: d,
    destroy: c
  };
}
function At(e, t, n, r = !1, o = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: o ? je() : null
  };
}
function Io(e) {
  const { history: t, location: n } = window, r = {
    value: kn(e, n)
  }, o = { value: t.state };
  o.value || i(r.value, {
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
  function i(l, d, a) {
    const c = e.indexOf("#"), f = c > -1 ? (n.host && document.querySelector("base") ? e : e.slice(c)) + l : Vo() + e + l;
    try {
      t[a ? "replaceState" : "pushState"](d, "", f), o.value = d;
    } catch (h) {
      P.NODE_ENV !== "production" ? S("Error with push/replace State", h) : console.error(h), n[a ? "replace" : "assign"](f);
    }
  }
  function s(l, d) {
    const a = V({}, t.state, At(
      o.value.back,
      // keep back and forward entries but override current position
      l,
      o.value.forward,
      !0
    ), d, { position: o.value.position });
    i(l, a, !0), r.value = l;
  }
  function u(l, d) {
    const a = V(
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

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), i(a.current, a, !0);
    const c = V({}, At(r.value, l, null), { position: a.position + 1 }, d);
    i(l, c, !1), r.value = l;
  }
  return {
    location: r,
    state: o,
    push: u,
    replace: s
  };
}
function Nn(e) {
  e = Sn(e);
  const t = Io(e), n = Co(e, t.state, t.location, t.replace);
  function r(i, s = !0) {
    s || n.pauseListeners(), history.go(i);
  }
  const o = V({
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
  function i(u, l, { direction: d, delta: a }) {
    const c = {
      direction: d,
      delta: a,
      type: fe.pop
    };
    for (const f of t)
      f(u, l, c);
  }
  const s = {
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
      r = Math.max(0, Math.min(r + u, n.length - 1)), l && i(this.location, d, {
        direction: a,
        delta: u
      });
    }
  };
  return Object.defineProperty(s, "location", {
    enumerable: !0,
    get: () => n[r]
  }), s;
}
function Ao(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), P.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && S(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), Nn(e);
}
function $e(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function Vn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const ut = Symbol(P.NODE_ENV !== "production" ? "navigation failure" : "");
var xt;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(xt || (xt = {}));
const xo = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${Do(t)}" via a navigation guard.`;
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
function de(e, t) {
  return P.NODE_ENV !== "production" ? V(new Error(xo[e](t)), {
    type: e,
    [ut]: !0
  }, t) : V(new Error(), {
    type: e,
    [ut]: !0
  }, t);
}
function q(e, t) {
  return e instanceof Error && ut in e && (t == null || !!(e.type & t));
}
const To = ["params", "query", "hash"];
function Do(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of To)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const Tt = "[^/]+?", jo = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Mo = /[.+*?^${}()[\]/\\]/g;
function Wo(e, t) {
  const n = V({}, jo, t), r = [];
  let o = n.start ? "^" : "";
  const i = [];
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
        c || (o += "/"), o += f.value.replace(Mo, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: g, repeatable: m, optional: v, regexp: w } = f;
        i.push({
          name: g,
          repeatable: m,
          optional: v
        });
        const b = w || Tt;
        if (b !== Tt) {
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
  const s = new RegExp(o, n.sensitive ? "" : "i");
  function u(d) {
    const a = d.match(s), c = {};
    if (!a)
      return null;
    for (let f = 1; f < a.length; f++) {
      const h = a[f] || "", g = i[f - 1];
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
    re: s,
    score: r,
    keys: i,
    parse: u,
    stringify: l
  };
}
function Bo(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Cn(e, t) {
  let n = 0;
  const r = e.score, o = t.score;
  for (; n < r.length && n < o.length; ) {
    const i = Bo(r[n], o[n]);
    if (i)
      return i;
    n++;
  }
  if (Math.abs(o.length - r.length) === 1) {
    if (Dt(r))
      return 1;
    if (Dt(o))
      return -1;
  }
  return o.length - r.length;
}
function Dt(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Lo = {
  type: 0,
  value: ""
}, Fo = /[a-zA-Z0-9_]/;
function Uo(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Lo]];
  if (!e.startsWith("/"))
    throw new Error(P.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const o = [];
  let i;
  function s() {
    i && o.push(i), i = [];
  }
  let u = 0, l, d = "", a = "";
  function c() {
    d && (n === 0 ? i.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (i.length > 1 && (l === "*" || l === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), i.push({
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
        l === "/" ? (d && c(), s()) : l === ":" ? (c(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        l === "(" ? n = 2 : Fo.test(l) ? f() : (c(), n = 0, l !== "*" && l !== "?" && l !== "+" && u--);
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
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), c(), s(), o;
}
function Ho(e, t, n) {
  const r = Wo(Uo(e.path), n);
  if (P.NODE_ENV !== "production") {
    const i = /* @__PURE__ */ new Set();
    for (const s of r.keys)
      i.has(s.name) && S(`Found duplicated params with name "${s.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), i.add(s.name);
  }
  const o = V(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !o.record.aliasOf == !t.record.aliasOf && t.children.push(o), o;
}
function Go(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = Bt({ strict: !1, end: !0, sensitive: !1 }, t);
  function o(c) {
    return r.get(c);
  }
  function i(c, f, h) {
    const g = !h, m = Mt(c);
    P.NODE_ENV !== "production" && Qo(m, f), m.aliasOf = h && h.record;
    const v = Bt(t, c), w = [m];
    if ("alias" in c) {
      const N = typeof c.alias == "string" ? [c.alias] : c.alias;
      for (const W of N)
        w.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          Mt(V({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: W,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let b, R;
    for (const N of w) {
      const { path: W } = N;
      if (f && W[0] !== "/") {
        const U = f.record.path, F = U[U.length - 1] === "/" ? "" : "/";
        N.path = f.record.path + (W && F + W);
      }
      if (P.NODE_ENV !== "production" && N.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (b = Ho(N, f, v), P.NODE_ENV !== "production" && f && W[0] === "/" && Yo(b, f), h ? (h.alias.push(b), P.NODE_ENV !== "production" && qo(h, b)) : (R = R || b, R !== b && R.alias.push(b), g && c.name && !Wt(b) && (P.NODE_ENV !== "production" && Jo(c, f), s(c.name))), In(b) && l(b), m.children) {
        const U = m.children;
        for (let F = 0; F < U.length; F++)
          i(U[F], b, h && h.children[F]);
      }
      h = h || b;
    }
    return R ? () => {
      s(R);
    } : we;
  }
  function s(c) {
    if (Vn(c)) {
      const f = r.get(c);
      f && (r.delete(c), n.splice(n.indexOf(f), 1), f.children.forEach(s), f.alias.forEach(s));
    } else {
      const f = n.indexOf(c);
      f > -1 && (n.splice(f, 1), c.record.name && r.delete(c.record.name), c.children.forEach(s), c.alias.forEach(s));
    }
  }
  function u() {
    return n;
  }
  function l(c) {
    const f = Xo(c, n);
    n.splice(f, 0, c), c.record.name && !Wt(c) && r.set(c.record.name, c);
  }
  function d(c, f) {
    let h, g = {}, m, v;
    if ("name" in c && c.name) {
      if (h = r.get(c.name), !h)
        throw de(1, {
          location: c
        });
      if (P.NODE_ENV !== "production") {
        const R = Object.keys(c.params || {}).filter((N) => !h.keys.find((W) => W.name === N));
        R.length && S(`Discarded invalid param(s) "${R.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, g = V(
        // paramsFromLocation is a new object
        jt(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((R) => !R.optional).concat(h.parent ? h.parent.keys.filter((R) => R.optional) : []).map((R) => R.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        c.params && jt(c.params, h.keys.map((R) => R.name))
      ), m = h.stringify(g);
    } else if (c.path != null)
      m = c.path, P.NODE_ENV !== "production" && !m.startsWith("/") && S(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((R) => R.re.test(m)), h && (g = h.parse(m), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((R) => R.re.test(f.path)), !h)
        throw de(1, {
          location: c,
          currentLocation: f
        });
      v = h.record.name, g = V({}, f.params, c.params), m = h.stringify(g);
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
      meta: Ko(w)
    };
  }
  e.forEach((c) => i(c));
  function a() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: i,
    resolve: d,
    removeRoute: s,
    clearRoutes: a,
    getRoutes: u,
    getRecordMatcher: o
  };
}
function jt(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function Mt(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: zo(e),
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
function zo(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function Wt(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Ko(e) {
  return e.reduce((t, n) => V(t, n.meta), {});
}
function Bt(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function lt(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function qo(e, t) {
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
function Jo(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function Yo(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(lt.bind(null, n)))
      return S(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function Xo(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const i = n + r >> 1;
    Cn(e, t[i]) < 0 ? r = i : n = i + 1;
  }
  const o = Zo(e);
  return o && (r = t.lastIndexOf(o, r - 1), P.NODE_ENV !== "production" && r < 0 && S(`Finding ancestor route "${o.record.path}" failed for "${e.record.path}"`)), r;
}
function Zo(e) {
  let t = e;
  for (; t = t.parent; )
    if (In(t) && Cn(e, t) === 0)
      return t;
}
function In({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function es(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let o = 0; o < r.length; ++o) {
    const i = r[o].replace(wn, " "), s = i.indexOf("="), u = le(s < 0 ? i : i.slice(0, s)), l = s < 0 ? null : le(i.slice(s + 1));
    if (u in t) {
      let d = t[u];
      L(d) || (d = t[u] = [d]), d.push(l);
    } else
      t[u] = l;
  }
  return t;
}
function Lt(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = mo(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (L(r) ? r.map((i) => i && at(i)) : [r && at(r)]).forEach((i) => {
      i !== void 0 && (t += (t.length ? "&" : "") + n, i != null && (t += "=" + i));
    });
  }
  return t;
}
function ts(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = L(r) ? r.map((o) => o == null ? null : "" + o) : r == null ? r : "" + r);
  }
  return t;
}
const ns = Symbol(P.NODE_ENV !== "production" ? "router view location matched" : ""), Ft = Symbol(P.NODE_ENV !== "production" ? "router view depth" : ""), Me = Symbol(P.NODE_ENV !== "production" ? "router" : ""), _t = Symbol(P.NODE_ENV !== "production" ? "route location" : ""), ft = Symbol(P.NODE_ENV !== "production" ? "router view location" : "");
function ve() {
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
function Z(e, t, n, r, o, i = (s) => s()) {
  const s = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[o] = r.enterCallbacks[o] || []);
  return () => new Promise((u, l) => {
    const d = (f) => {
      f === !1 ? l(de(4, {
        from: n,
        to: t
      })) : f instanceof Error ? l(f) : $e(f) ? l(de(2, {
        from: t,
        to: f
      })) : (s && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[o] === s && typeof f == "function" && s.push(f), u());
    }, a = i(() => e.call(r && r.instances[o], t, n, P.NODE_ENV !== "production" ? rs(d, t, n) : d));
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
function rs(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && S(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function Qe(e, t, n, r, o = (i) => i()) {
  const i = [];
  for (const s of e) {
    P.NODE_ENV !== "production" && !s.components && !s.children.length && S(`Record with path "${s.path}" is either missing a "component(s)" or "children" property.`);
    for (const u in s.components) {
      let l = s.components[u];
      if (P.NODE_ENV !== "production") {
        if (!l || typeof l != "object" && typeof l != "function")
          throw S(`Component "${u}" in record with path "${s.path}" is not a valid component. Received "${String(l)}".`), new Error("Invalid route component");
        if ("then" in l) {
          S(`Component "${u}" in record with path "${s.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = l;
          l = () => d;
        } else l.__asyncLoader && // warn only once per component
        !l.__warnedDefineAsync && (l.__warnedDefineAsync = !0, S(`Component "${u}" in record with path "${s.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !s.instances[u]))
        if (yn(l)) {
          const a = (l.__vccOpts || l)[t];
          a && i.push(Z(a, n, r, s, u, o));
        } else {
          let d = l();
          P.NODE_ENV !== "production" && !("catch" in d) && (S(`Component "${u}" in record with path "${s.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), i.push(() => d.then((a) => {
            if (!a)
              throw new Error(`Couldn't resolve component "${u}" at "${s.path}"`);
            const c = oo(a) ? a.default : a;
            s.mods[u] = a, s.components[u] = c;
            const h = (c.__vccOpts || c)[t];
            return h && Z(h, n, r, s, u, o)();
          }));
        }
    }
  }
  return i;
}
function Ut(e) {
  const t = K(Me), n = K(_t);
  let r = !1, o = null;
  const i = T(() => {
    const a = M(e.to);
    return P.NODE_ENV !== "production" && (!r || a !== o) && ($e(a) || (r ? S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- previous to:`, o, `
- props:`, e) : S(`Invalid value for prop "to" in useLink()
- to:`, a, `
- props:`, e)), o = a, r = !0), t.resolve(a);
  }), s = T(() => {
    const { matched: a } = i.value, { length: c } = a, f = a[c - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const g = h.findIndex(ee.bind(null, f));
    if (g > -1)
      return g;
    const m = Ht(a[c - 2]);
    return (
      // we are dealing with nested routes
      c > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      Ht(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(ee.bind(null, a[c - 2])) : g
    );
  }), u = T(() => s.value > -1 && cs(n.params, i.value.params)), l = T(() => s.value > -1 && s.value === n.matched.length - 1 && Pn(n.params, i.value.params));
  function d(a = {}) {
    if (as(a)) {
      const c = t[M(e.replace) ? "replace" : "push"](
        M(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(we);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => c), c;
    }
    return Promise.resolve();
  }
  if (P.NODE_ENV !== "production" && Q) {
    const a = Xt();
    if (a) {
      const c = {
        route: i.value,
        isActive: u.value,
        isExactActive: l.value,
        error: null
      };
      a.__vrl_devtools = a.__vrl_devtools || [], a.__vrl_devtools.push(c), Jt(() => {
        c.route = i.value, c.isActive = u.value, c.isExactActive = l.value, c.error = $e(M(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: i,
    href: T(() => i.value.href),
    isActive: u,
    isExactActive: l,
    navigate: d
  };
}
function os(e) {
  return e.length === 1 ? e[0] : e;
}
const ss = /* @__PURE__ */ D({
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
  useLink: Ut,
  setup(e, { slots: t }) {
    const n = er(Ut(e)), { options: r } = K(Me), o = T(() => ({
      [Gt(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [Gt(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const i = t.default && os(t.default(n));
      return e.custom ? i : A("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: o.value
      }, i);
    };
  }
}), is = ss;
function as(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function cs(e, t) {
  for (const n in t) {
    const r = t[n], o = e[n];
    if (typeof r == "string") {
      if (r !== o)
        return !1;
    } else if (!L(o) || o.length !== r.length || r.some((i, s) => i !== o[s]))
      return !1;
  }
  return !0;
}
function Ht(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const Gt = (e, t, n) => e ?? t ?? n, us = /* @__PURE__ */ D({
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
    P.NODE_ENV !== "production" && fs();
    const r = K(ft), o = T(() => e.route || r.value), i = K(Ft, 0), s = T(() => {
      let d = M(i);
      const { matched: a } = o.value;
      let c;
      for (; (c = a[d]) && !c.components; )
        d++;
      return d;
    }), u = T(() => o.value.matched[s.value]);
    ue(Ft, T(() => s.value + 1)), ue(ns, u), ue(ft, o);
    const l = Y();
    return z(() => [l.value, u.value, e.name], ([d, a, c], [f, h, g]) => {
      a && (a.instances[c] = d, h && h !== a && d && d === f && (a.leaveGuards.size || (a.leaveGuards = h.leaveGuards), a.updateGuards.size || (a.updateGuards = h.updateGuards))), d && a && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !ee(a, h) || !f) && (a.enterCallbacks[c] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = o.value, a = e.name, c = u.value, f = c && c.components[a];
      if (!f)
        return zt(n.default, { Component: f, route: d });
      const h = c.props[a], g = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = A(f, V({}, g, t, {
        onVnodeUnmounted: (w) => {
          w.component.isUnmounted && (c.instances[a] = null);
        },
        ref: l
      }));
      if (P.NODE_ENV !== "production" && Q && v.ref) {
        const w = {
          depth: s.value,
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
        zt(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function zt(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const ls = us;
function fs() {
  const e = Xt(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
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
function ye(e, t) {
  const n = V({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => bs(r, ["instances", "children", "aliasOf"]))
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
let ds = 0;
function hs(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = ds++;
  ro({
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
        value: ye(t.currentRoute.value, "Current Route")
      });
    }), o.on.visitComponentTree(({ treeNode: a, componentInstance: c }) => {
      if (c.__vrv_devtools) {
        const f = c.__vrv_devtools;
        a.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: $n
        });
      }
      L(c.__vrl_devtools) && (c.__devtoolsApi = o, c.__vrl_devtools.forEach((f) => {
        let h = f.route.path, g = Tn, m = "", v = 0;
        f.error ? (h = f.error, g = ys, v = _s) : f.isExactActive ? (g = xn, m = "This is exactly active") : f.isActive && (g = An, m = "This link is active"), a.tags.push({
          label: h,
          textColor: v,
          tooltip: m,
          backgroundColor: g
        });
      }));
    }), z(t.currentRoute, () => {
      l(), o.notifyComponentUpdate(), o.sendInspectorTree(u), o.sendInspectorState(u);
    });
    const i = "router:navigations:" + r;
    o.addTimelineLayer({
      id: i,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((a, c) => {
      o.addTimelineEvent({
        layerId: i,
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
    let s = 0;
    t.beforeEach((a, c) => {
      const f = {
        guard: ke("beforeEach"),
        from: ye(c, "Current Location during this navigation"),
        to: ye(a, "Target location")
      };
      Object.defineProperty(a.meta, "__navigationId", {
        value: s++
      }), o.addTimelineEvent({
        layerId: i,
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
      }, h.status = ke("❌")) : h.status = ke("✅"), h.from = ye(c, "Current Location during this navigation"), h.to = ye(a, "Target location"), o.addTimelineEvent({
        layerId: i,
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
          options: gs(f)
        });
      }
    }), o.sendInspectorTree(u), o.sendInspectorState(u);
  });
}
function ps(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function gs(e) {
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
        display: e.keys.map((r) => `${r.name}${ps(r)}`).join(" "),
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
const $n = 15485081, An = 2450411, xn = 8702998, ms = 2282478, Tn = 16486972, vs = 6710886, ys = 16704226, _s = 12131356;
function Dn(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: ms
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: Tn
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: $n
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: xn
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: An
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: vs
  });
  let r = n.__vd_id;
  return r == null && (r = String(ws++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(Dn)
  };
}
let ws = 0;
const Es = /^\/(.*)\/([a-z]*)$/;
function jn(e, t) {
  const n = t.matched.length && ee(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => ee(r, e.record))), e.children.forEach((r) => jn(r, t));
}
function Mn(e) {
  e.__vd_match = !1, e.children.forEach(Mn);
}
function dt(e, t) {
  const n = String(e.re).match(Es);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((s) => dt(s, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const o = e.record.path.toLowerCase(), i = le(o);
  return !t.startsWith("/") && (i.includes(t) || o.includes(t)) || i.startsWith(t) || o.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((s) => dt(s, t));
}
function bs(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function Rs(e) {
  const t = Go(e.routes, e), n = e.parseQuery || es, r = e.stringifyQuery || Lt, o = e.history;
  if (P.NODE_ENV !== "production" && !o)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const i = ve(), s = ve(), u = ve(), l = H(X);
  let d = X;
  Q && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const a = ze.bind(null, (p) => "" + p), c = ze.bind(null, yo), f = (
    // @ts-expect-error: intentionally avoid the type check
    ze.bind(null, le)
  );
  function h(p, _) {
    let y, E;
    return Vn(p) ? (y = t.getRecordMatcher(p), P.NODE_ENV !== "production" && !y && S(`Parent route "${String(p)}" not found when adding child route`, _), E = _) : E = p, t.addRoute(E, y);
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
    if (_ = V({}, _ || l.value), typeof p == "string") {
      const O = Ke(n, p, _.path), I = t.resolve({ path: O.path }, _), te = o.createHref(O.fullPath);
      return P.NODE_ENV !== "production" && (te.startsWith("//") ? S(`Location "${p}" resolved to "${te}". A resolved location cannot start with multiple slashes.`) : I.matched.length || S(`No match found for location with path "${p}"`)), V(O, I, {
        params: f(I.params),
        hash: le(O.hash),
        redirectedFrom: void 0,
        href: te
      });
    }
    if (P.NODE_ENV !== "production" && !$e(p))
      return S(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), w({});
    let y;
    if (p.path != null)
      P.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && S(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), y = V({}, p, {
        path: Ke(n, p.path, _.path).path
      });
    else {
      const O = V({}, p.params);
      for (const I in O)
        O[I] == null && delete O[I];
      y = V({}, p, {
        params: c(O)
      }), _.params = c(_.params);
    }
    const E = t.resolve(y, _), C = p.hash || "";
    P.NODE_ENV !== "production" && C && !C.startsWith("#") && S(`A \`hash\` should always start with the character "#". Replace "${C}" with "#${C}".`), E.params = a(f(E.params));
    const $ = Eo(r, V({}, p, {
      hash: go(C),
      path: E.path
    })), k = o.createHref($);
    return P.NODE_ENV !== "production" && (k.startsWith("//") ? S(`Location "${p}" resolved to "${k}". A resolved location cannot start with multiple slashes.`) : E.matched.length || S(`No match found for location with path "${p.path != null ? p.path : p}"`)), V({
      fullPath: $,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: C,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === Lt ? ts(p.query) : p.query || {}
      )
    }, E, {
      redirectedFrom: void 0,
      href: k
    });
  }
  function b(p) {
    return typeof p == "string" ? Ke(n, p, l.value.path) : V({}, p);
  }
  function R(p, _) {
    if (d !== p)
      return de(8, {
        from: _,
        to: p
      });
  }
  function N(p) {
    return F(p);
  }
  function W(p) {
    return N(V(b(p), { replace: !0 }));
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
      return V({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: E.path != null ? {} : p.params
      }, E);
    }
  }
  function F(p, _) {
    const y = d = w(p), E = l.value, C = p.state, $ = p.force, k = p.replace === !0, O = U(y);
    if (O)
      return F(
        V(b(O), {
          state: typeof O == "object" ? V({}, C, O.state) : C,
          force: $,
          replace: k
        }),
        // keep original redirectedFrom if it exists
        _ || y
      );
    const I = y;
    I.redirectedFrom = _;
    let te;
    return !$ && Ct(r, E, y) && (te = de(16, { to: I, from: E }), Pt(
      E,
      E,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (te ? Promise.resolve(te) : wt(I, E)).catch((j) => q(j) ? (
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
          Ct(r, w(j.to), I) && // and we have done it a couple of times
          _ && // @ts-expect-error: added only in dev
          (_._count = _._count ? (
            // @ts-expect-error
            _._count + 1
          ) : 1) > 30 ? (S(`Detected a possibly infinite redirection in a navigation guard when going from "${E.fullPath}" to "${I.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : F(
            // keep options
            V({
              // preserve an existing replacement but allow the redirect to override it
              replace: k
            }, b(j.to), {
              state: typeof j.to == "object" ? V({}, C, j.to.state) : C,
              force: $
            }),
            // preserve the original redirectedFrom if any
            _ || I
          );
      } else
        j = bt(I, E, !0, k, C);
      return Et(I, E, j), j;
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
  function wt(p, _) {
    let y;
    const [E, C, $] = Ps(p, _);
    y = Qe(E.reverse(), "beforeRouteLeave", p, _);
    for (const O of E)
      O.leaveGuards.forEach((I) => {
        y.push(Z(I, p, _));
      });
    const k = zn.bind(null, p, _);
    return y.push(k), se(y).then(() => {
      y = [];
      for (const O of i.list())
        y.push(Z(O, p, _));
      return y.push(k), se(y);
    }).then(() => {
      y = Qe(C, "beforeRouteUpdate", p, _);
      for (const O of C)
        O.updateGuards.forEach((I) => {
          y.push(Z(I, p, _));
        });
      return y.push(k), se(y);
    }).then(() => {
      y = [];
      for (const O of $)
        if (O.beforeEnter)
          if (L(O.beforeEnter))
            for (const I of O.beforeEnter)
              y.push(Z(I, p, _));
          else
            y.push(Z(O.beforeEnter, p, _));
      return y.push(k), se(y);
    }).then(() => (p.matched.forEach((O) => O.enterCallbacks = {}), y = Qe($, "beforeRouteEnter", p, _, We), y.push(k), se(y))).then(() => {
      y = [];
      for (const O of s.list())
        y.push(Z(O, p, _));
      return y.push(k), se(y);
    }).catch((O) => q(
      O,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? O : Promise.reject(O));
  }
  function Et(p, _, y) {
    u.list().forEach((E) => We(() => E(p, _, y)));
  }
  function bt(p, _, y, E, C) {
    const $ = R(p, _);
    if ($)
      return $;
    const k = _ === X, O = Q ? history.state : {};
    y && (E || k ? o.replace(p.fullPath, V({
      scroll: k && O && O.scroll
    }, C)) : o.push(p.fullPath, C)), l.value = p, Pt(p, _, y, k), Fe();
  }
  let ge;
  function Kn() {
    ge || (ge = o.listen((p, _, y) => {
      if (!St.listening)
        return;
      const E = w(p), C = U(E);
      if (C) {
        F(V(C, { replace: !0, force: !0 }), E).catch(we);
        return;
      }
      d = E;
      const $ = l.value;
      Q && ko($t($.fullPath, y.delta), je()), wt(E, $).catch((k) => q(
        k,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? k : q(
        k,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (F(
        V(b(k.to), {
          force: !0
        }),
        E
        // avoid an uncaught rejection, let push call triggerError
      ).then((O) => {
        q(
          O,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !y.delta && y.type === fe.pop && o.go(-1, !1);
      }).catch(we), Promise.reject()) : (y.delta && o.go(-y.delta, !1), Le(k, E, $))).then((k) => {
        k = k || bt(
          // after navigation, all matched components are resolved
          E,
          $,
          !1
        ), k && (y.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !q(
          k,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? o.go(-y.delta, !1) : y.type === fe.pop && q(
          k,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && o.go(-1, !1)), Et(E, $, k);
      }).catch(we);
    }));
  }
  let Be = ve(), Rt = ve(), Se;
  function Le(p, _, y) {
    Fe(p);
    const E = Rt.list();
    return E.length ? E.forEach((C) => C(p, _, y)) : (P.NODE_ENV !== "production" && S("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function qn() {
    return Se && l.value !== X ? Promise.resolve() : new Promise((p, _) => {
      Be.add([p, _]);
    });
  }
  function Fe(p) {
    return Se || (Se = !p, Kn(), Be.list().forEach(([_, y]) => p ? y(p) : _()), Be.reset()), p;
  }
  function Pt(p, _, y, E) {
    const { scrollBehavior: C } = e;
    if (!Q || !C)
      return Promise.resolve();
    const $ = !y && No($t(p.fullPath, 0)) || (E || !y) && history.state && history.state.scroll || null;
    return Ne().then(() => C(p, _, $)).then((k) => k && Oo(k)).catch((k) => Le(k, p, _));
  }
  const Ue = (p) => o.go(p);
  let He;
  const Oe = /* @__PURE__ */ new Set(), St = {
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
    replace: W,
    go: Ue,
    back: () => Ue(-1),
    forward: () => Ue(1),
    beforeEach: i.add,
    beforeResolve: s.add,
    afterEach: u.add,
    onError: Rt.add,
    isReady: qn,
    install(p) {
      const _ = this;
      p.component("RouterLink", is), p.component("RouterView", ls), p.config.globalProperties.$router = _, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => M(l)
      }), Q && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !He && l.value === X && (He = !0, N(o.location).catch((C) => {
        P.NODE_ENV !== "production" && S("Unexpected error when starting the router:", C);
      }));
      const y = {};
      for (const C in X)
        Object.defineProperty(y, C, {
          get: () => l.value[C],
          enumerable: !0
        });
      p.provide(Me, _), p.provide(_t, Zn(y)), p.provide(ft, l);
      const E = p.unmount;
      Oe.add(p), p.unmount = function() {
        Oe.delete(p), Oe.size < 1 && (d = X, ge && ge(), ge = null, l.value = X, He = !1, Se = !1), E();
      }, P.NODE_ENV !== "production" && Q && hs(p, _, t);
    }
  };
  function se(p) {
    return p.reduce((_, y) => _.then(() => We(y)), Promise.resolve());
  }
  return St;
}
function Ps(e, t) {
  const n = [], r = [], o = [], i = Math.max(t.matched.length, e.matched.length);
  for (let s = 0; s < i; s++) {
    const u = t.matched[s];
    u && (e.matched.find((d) => ee(d, u)) ? r.push(u) : n.push(u));
    const l = e.matched[s];
    l && (t.matched.find((d) => ee(d, l)) || o.push(l));
  }
  return [n, r, o];
}
function Ss() {
  return K(Me);
}
function Os(e) {
  return K(_t);
}
function ks(e) {
  const { immediately: t = !1, code: n } = e;
  let r = B(n);
  return t && (r = r()), r;
}
const Ee = /* @__PURE__ */ new Map();
function Ns(e) {
  if (!Ee.has(e)) {
    const t = Symbol();
    return Ee.set(e, t), t;
  }
  return Ee.get(e);
}
function pe(e, t) {
  var u, l;
  const n = Ge(e), r = Cs(n, t);
  if (r.size > 0) {
    const d = Ns(e);
    ue(d, r);
  }
  const o = oe({ attached: { varMap: r, sid: e } });
  Dr({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: o,
    sid: e
  }), (u = n.js_watch) == null || u.forEach((d) => {
    Kr(d, o);
  }), (l = n.vue_watch) == null || l.forEach((d) => {
    zr(d, o);
  });
  function i(d, a) {
    const c = Ge(d);
    if (!c.vfor)
      return;
    const { fi: f } = c.vfor;
    f && (r.get(f.id).value = a.index);
  }
  function s(d) {
    const { sid: a, value: c } = d;
    if (!a)
      return;
    const f = Ge(a), { id: h } = f.sp, g = r.get(h);
    g.value = c;
  }
  return {
    updateVforInfo: i,
    updateSlotPropValue: s
  };
}
function oe(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, o, i] = Is(n);
  t && r.set(t.sid, t.varMap);
  const s = o ? Os() : null, u = i ? Ss() : null, l = o ? () => s : () => {
    throw new Error("Route params not found");
  }, d = i ? () => u : () => {
    throw new Error("Router not found");
  };
  function a(m) {
    const v = Ye(f(m));
    return un(v, m.path ?? [], a);
  }
  function c(m) {
    const v = f(m);
    return Er(v, {
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
        ln(w.value, m.path, v, a);
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
function Cs(e, t) {
  var o, i, s, u, l, d;
  const n = /* @__PURE__ */ new Map(), r = oe({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((a) => {
    n.set(a.id, a.value);
  }), e.jsFn && e.jsFn.forEach((a) => {
    const c = ks(a);
    n.set(a.id, () => c);
  }), e.vfor && (t != null && t.initVforInfo)) {
    const { fv: a, fi: c, fk: f } = e.vfor, { index: h = 0, keyValue: g = null, config: m } = t.initVforInfo, { sid: v } = m, w = Qr(v);
    if (a) {
      const b = ce(() => ({
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
  return (i = e.eRefs) == null || i.forEach((a) => {
    n.set(a.id, H(null));
  }), (s = e.refs) == null || s.forEach((a) => {
    const c = br(a);
    n.set(a.id, c);
  }), (u = e.web_computed) == null || u.forEach((a) => {
    const c = Pr(a);
    n.set(a.id, c);
  }), (l = e.js_computed) == null || l.forEach((a) => {
    const c = Sr(
      a,
      r
    );
    n.set(a.id, c);
  }), (d = e.vue_computed) == null || d.forEach((a) => {
    const c = Rr(
      a,
      r
    );
    n.set(a.id, c);
  }), n;
}
function Is(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: o = !0 } = e;
    for (const i of n)
      t.set(i, Vs(i));
    return [t, r, o];
  }
  for (const n of Ee.keys()) {
    const r = Wn(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const $s = D(As, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function As(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = pe(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? he(n[0]) : n.map((o) => he(o)));
}
function Kt(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let o = [];
  if (r > 0)
    for (let i = t; i < n; i += r)
      o.push(i);
  else
    for (let i = t; i > n; i += r)
      o.push(i);
  return o;
}
const Bn = D(xs, {
  props: ["config"]
});
function xs(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = oe(), i = js(t ?? "index"), s = Ms(e.config, r);
  return qr(e.config, s), () => {
    const u = tr(s.value, (...l) => {
      const d = l[0], a = l[2] !== void 0, c = a ? l[2] : l[1], f = a ? l[1] : c, h = i(d, c);
      return A($s, {
        key: h,
        vforValue: d,
        vforIndex: c,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? A(Zt, n, {
      default: () => u
    }) : u;
  };
}
const Ts = (e) => e, Ds = (e, t) => t;
function js(e) {
  const t = vr(e);
  return typeof t == "function" ? t : e === "item" ? Ts : Ds;
}
function Ms(e, t) {
  const { type: n, value: r } = e.array, o = n === ot.range;
  if (n === ot.const || o && typeof r == "number") {
    const s = o ? Kt({
      end: Math.max(0, r)
    }) : r;
    return ce(() => ({
      get() {
        return s;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (o) {
    const s = r, u = t.getVueRefObject(s);
    return ce(() => ({
      get() {
        return Kt({
          end: Math.max(0, u.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return ce(() => {
    const s = t.getVueRefObject(
      r
    );
    return {
      get() {
        return s.value;
      },
      set(u) {
        s.value = u;
      }
    };
  });
}
const Ln = D(Ws, {
  props: ["config"]
});
function Ws(e) {
  const { sid: t, items: n, on: r } = e.config;
  Pe(t) && pe(t);
  const o = oe();
  return () => (typeof r == "boolean" ? r : o.getValue(r)) ? n.map((s) => he(s)) : void 0;
}
const qt = D(Bs, {
  props: ["slotConfig"]
});
function Bs(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Pe(t) && pe(t), () => n.map((r) => he(r));
}
const Je = ":default", Fn = D(Ls, {
  props: ["config"]
});
function Ls(e) {
  const { on: t, caseValues: n, slots: r, sid: o } = e.config;
  Pe(o) && pe(o);
  const i = oe();
  return () => {
    const s = i.getValue(t), u = n.map((l, d) => {
      const a = d.toString(), c = r[a];
      return l === s ? A(qt, { slotConfig: c, key: a }) : null;
    }).filter(Boolean);
    return u.length === 0 && Je in r ? A(qt, {
      slotConfig: r[Je],
      key: Je
    }) : u;
  };
}
const Fs = "on:mounted";
function Us(e, t, n) {
  const r = Object.assign(
    {},
    ...Object.entries(t ?? {}).map(([s, u]) => {
      const l = u.map((a) => {
        if (a.type === "web") {
          const c = Hs(a, n);
          return Gs(a, c, n);
        } else {
          if (a.type === "vue")
            return Ks(a, n);
          if (a.type === "js")
            return zs(a, n);
        }
        throw new Error(`unknown event type ${a}`);
      });
      if (l.length === 1)
        return { [s]: l[0] };
      const d = (...a) => l.forEach((c) => {
        Promise.resolve().then(() => c(...a));
      });
      return { [s]: d };
    })
  ), { [Fs]: o, ...i } = r;
  return e = Ve(e, i), o && (e = en(e, [
    [
      {
        mounted(s) {
          o(s);
        }
      }
    ]
  ])), e;
}
function Hs(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: o, type: i }) => {
    if (i === G.EventContext) {
      const { path: s } = o;
      if (s.startsWith(":")) {
        const u = s.slice(1);
        return B(u)(...r);
      }
      return Hr(r[0], s.split("."));
    }
    return i === G.Ref ? t.getValue(o) : o;
  });
}
function Gs(e, t, n) {
  async function r(...o) {
    const i = t(...o), s = pn({
      config: e.preSetup,
      varGetter: n
    });
    try {
      s.run();
      const u = await hn().eventSend(e, i);
      if (!u)
        return;
      Te(u, e.sets, n);
    } finally {
      s.tryReset();
    }
  }
  return r;
}
function zs(e, t) {
  const { sets: n, code: r, inputs: o = [] } = e, i = B(r);
  function s(...u) {
    const l = o.map(({ value: a, type: c }) => {
      if (c === G.EventContext) {
        if (a.path.startsWith(":")) {
          const f = a.path.slice(1);
          return B(f)(...u);
        }
        return Ur(u[0], a.path.split("."));
      }
      if (c === G.Ref)
        return mn(t.getValue(a));
      if (c === G.Data)
        return a;
      if (c === G.JsFn)
        return t.getValue(a);
      throw new Error(`unknown input type ${c}`);
    }), d = i(...l);
    if (n !== void 0) {
      const c = n.length === 1 ? [d] : d, f = c.map((h) => h === void 0 ? 1 : 0);
      Te(
        { values: c, types: f },
        n,
        t
      );
    }
  }
  return s;
}
function Ks(e, t) {
  const { code: n, inputs: r = {} } = e, o = De(
    r,
    (u) => u.type !== G.Data ? t.getVueRefObject(u.value) : u.value
  ), i = B(n, o);
  function s(...u) {
    i(...u);
  }
  return s;
}
function qs(e, t) {
  const n = [];
  (e.bStyle || []).forEach((i) => {
    Array.isArray(i) ? n.push(
      ...i.map((s) => t.getValue(s))
    ) : n.push(
      De(
        i,
        (s) => t.getValue(s)
      )
    );
  });
  const r = nr([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function Qs(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return Ce(n);
  const { str: r, map: o, bind: i } = n, s = [];
  return r && s.push(r), o && s.push(
    De(
      o,
      (u) => t.getValue(u)
    )
  ), i && s.push(...i.map((u) => t.getValue(u))), Ce(s);
}
function Ae(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => Ae(n, !0));
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
        t && Ae(r, !0);
  }
}
function Js(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = B(t)), { name: e, value: t, isFunc: n };
}
function Ys(e, t, n) {
  var o;
  const r = {};
  return kt(e.bProps || {}, (i, s) => {
    const u = n.getValue(i);
    Re(u) || (Ae(u), r[s] = Xs(u, s));
  }), (o = e.proxyProps) == null || o.forEach((i) => {
    const s = n.getValue(i);
    typeof s == "object" && kt(s, (u, l) => {
      const { name: d, value: a } = Js(l, u);
      r[d] = a;
    });
  }), { ...t, ...r };
}
function Xs(e, t) {
  return t === "innerText" ? xe(e) : e;
}
const Zs = D(ei, {
  props: ["slotPropValue", "config"]
});
function ei(e) {
  const { sid: t, items: n } = e.config, r = Pe(t) ? pe(t, {
    initSlotPropInfo: {
      value: e.slotPropValue
    }
  }).updateSlotPropValue : ti;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((o) => he(o)));
}
function ti() {
}
function ni(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? ht(n[":"]) : gn(n, { keyFn: (s) => s === ":" ? "default" : s, valueFn: (s) => (u) => s.use_prop ? ri(u, s) : ht(s) });
}
function ri(e, t) {
  return A(Zs, { config: t, slotPropValue: e });
}
function oi(e, t, n) {
  const r = [], { dir: o = [] } = t;
  return o.forEach((i) => {
    const { sys: s, name: u, arg: l, value: d, mf: a } = i;
    if (u === "vmodel") {
      const c = n.getVueRefObject(d);
      if (e = Ve(e, {
        [`onUpdate:${l}`]: (f) => {
          c.value = f;
        }
      }), s === 1) {
        const f = a ? Object.fromEntries(a.map((h) => [h, !0])) : {};
        r.push([rr, c.value, void 0, f]);
      } else
        e = Ve(e, {
          [l]: c.value
        });
    } else if (u === "vshow") {
      const c = n.getVueRefObject(d);
      r.push([or, c.value]);
    } else
      console.warn(`Directive ${u} is not supported yet`);
  }), en(e, r);
}
function si(e, t, n) {
  const { eRef: r } = t;
  return r ? Ve(e, { ref: n.getVueRefObject(r) }) : e;
}
const Un = Symbol();
function ii(e) {
  ue(Un, e);
}
function Mi() {
  return K(Un);
}
const ai = D(ci, {
  props: ["config"]
});
function ci(e) {
  const { config: t } = e, n = oe({
    sidCollector: new ui(t).getCollectInfo()
  });
  t.varGetterStrategy && ii(n);
  const r = t.props ?? {};
  return Ae(r, !0), () => {
    const { tag: o } = t, i = typeof o == "string" ? o : n.getValue(o), s = sr(i), u = typeof s == "string", l = Qs(t, n), { styles: d, hasStyle: a } = qs(t, n), c = ni(t, u), f = Ys(t, r, n), h = ir(f) || {};
    a && (h.style = d), l && (h.class = l);
    let g = A(s, { ...h }, c);
    return g = Us(g, t.events ?? {}, n), g = si(g, t, n), oi(g, t, n);
  };
}
class ui {
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
      proxyProps: i,
      bStyle: s,
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
      }), i && i.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), s && s.forEach((d) => {
        Array.isArray(d) ? d.forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        }) : Object.values(d).forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        });
      }), u && Object.values(u).forEach((d) => {
        this._handleEventInputs(d), this._handleEventSets(d);
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
    fn(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { inputs: r } = n;
        r == null || r.forEach((o) => {
          if (o.type === G.Ref) {
            const i = o.value;
            this._tryExtractSidToCollection(i), this._extendWithPaths(i);
          }
        });
      } else if (n.type === "vue") {
        const { inputs: r } = n;
        if (r) {
          const o = Object.values(r);
          o == null || o.forEach((i) => {
            if (i.type === G.Ref) {
              const s = i.value;
              this._tryExtractSidToCollection(s), this._extendWithPaths(s);
            }
          });
        }
      }
    });
  }
  _handleEventSets(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { sets: r } = n;
        r == null || r.forEach((o) => {
          vt(o.ref) && (this.sids.add(o.ref.sid), this._extendWithPaths(o.ref));
        });
      }
    });
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (_r(r)) {
        const o = wr(r);
        this._tryExtractSidToCollection(o), o.path && n.push(...o.path);
      }
    }
  }
}
function he(e, t) {
  return Or(e) ? A(Bn, { config: e, key: t }) : kr(e) ? A(Ln, { config: e, key: t }) : Nr(e) ? A(Fn, { config: e, key: t }) : A(ai, { config: e, key: t });
}
function ht(e, t) {
  return A(Hn, { slotConfig: e, key: t });
}
const Hn = D(li, {
  props: ["slotConfig"]
});
function li(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Pe(t) && pe(t), () => n.map((r) => he(r));
}
function fi(e, t) {
  const { state: n, isReady: r, isLoading: o } = mr(async () => {
    let i = e;
    const s = t;
    if (!i && !s)
      throw new Error("Either config or configUrl must be provided");
    if (!i && s && (i = await (await fetch(s)).json()), !i)
      throw new Error("Failed to load config");
    return i;
  }, {});
  return { config: n, isReady: r, isLoading: o };
}
function di(e) {
  const t = Y(!1), n = Y("");
  function r(o, i) {
    let s;
    return i.component ? s = `Error captured from component:tag: ${i.component.tag} ; id: ${i.component.id} ` : s = "Error captured from app init", console.group(s), console.error("Component:", i.component), console.error("Error:", o), console.groupEnd(), e && (t.value = !0, n.value = `${s} ${o.message}`), !1;
  }
  return ar(r), { hasError: t, errorMessage: n };
}
let pt;
function hi(e) {
  if (e === "web" || e === "webview") {
    pt = pi;
    return;
  }
  if (e === "zero") {
    pt = gi;
    return;
  }
  throw new Error(`Unsupported mode: ${e}`);
}
function pi(e) {
  const { assetPath: t = "/assets/icons", icon: n = "" } = e, [r, o] = n.split(":");
  return {
    assetPath: t,
    svgName: `${r}.svg`
  };
}
function gi() {
  return {
    assetPath: "",
    svgName: ""
  };
}
function mi(e, t) {
  const n = T(() => {
    const s = e.value;
    if (!s)
      return null;
    const d = new DOMParser().parseFromString(s, "image/svg+xml").querySelector("svg");
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
  }), { size: r, color: o } = t, i = T(() => {
    const s = {};
    return r.value !== null && r.value !== void 0 && (s.width = r.value.toString(), s.height = r.value.toString()), o.value !== null && o.value !== void 0 && (s.fill = o.value), {
      ...n.value,
      ...s
    };
  });
  return () => {
    if (!n.value)
      return null;
    const s = i.value;
    return A("svg", s);
  };
}
const vi = {
  class: "app-box insta-themes",
  "data-scaling": "100%"
}, yi = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, _i = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, wi = /* @__PURE__ */ D({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: o } = fi(
      t.config,
      t.configUrl
    );
    z(r, (u) => {
      u.url && (dr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: u.url.path,
        pathParams: u.url.params,
        webServerInfo: u.webInfo
      }), Ar(t.meta.mode)), hi(t.meta.mode), hr(u);
    });
    const { hasError: i, errorMessage: s } = di(n);
    return (u, l) => (J(), ne("div", vi, [
      M(o) ? (J(), ne("div", yi, l[0] || (l[0] = [
        tn("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (J(), ne("div", {
        key: 1,
        class: Ce(["insta-main", M(r).class])
      }, [
        cr(M(Hn), { "slot-config": M(r) }, null, 8, ["slot-config"]),
        M(i) ? (J(), ne("div", _i, xe(M(s)), 1)) : Xe("", !0)
      ], 2))
    ]));
  }
});
function Ei(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => A(
    Zt,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const bi = D(Ei, {
  props: ["name", "tag"]
});
function Ri(e) {
  const { content: t, r: n = 0 } = e, r = oe(), o = n === 1 ? () => r.getValue(t) : () => t;
  return () => xe(o());
}
const Pi = D(Ri, {
  props: ["content", "r"]
});
function Si(e) {
  return `i-size-${e}`;
}
function Oi(e) {
  return e ? `i-weight-${e}` : "";
}
function ki(e) {
  return e ? `i-text-align-${e}` : "";
}
const Ni = /* @__PURE__ */ D({
  __name: "Heading",
  props: {
    text: {},
    size: {},
    weight: {},
    align: {}
  },
  setup(e) {
    const t = e, n = T(() => [
      Si(t.size ?? "6"),
      Oi(t.weight),
      ki(t.align)
    ]);
    return (r, o) => (J(), ne("h1", {
      class: Ce(["insta-Heading", n.value])
    }, xe(r.text), 3));
  }
}), Vi = /* @__PURE__ */ D({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (J(), nn(ur, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      lr(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), Ci = ["width", "height", "fill"], Ii = ["xlink:href"], $i = /* @__PURE__ */ D({
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
    const t = e, { assetPath: n, svgName: r } = pt(t), o = ie(() => t.icon ? t.icon.split(":")[1] : ""), i = ie(() => t.size || "1em"), s = ie(() => t.color || "currentColor"), u = ie(() => t.rawSvg || null), l = T(() => `${n}/${r}/#${o.value}`), d = mi(u, {
      size: ie(() => t.size),
      color: ie(() => t.color)
    });
    return (a, c) => (J(), ne(rn, null, [
      o.value ? (J(), ne("svg", {
        key: 0,
        width: i.value,
        height: i.value,
        fill: s.value
      }, [
        tn("use", { "xlink:href": l.value }, null, 8, Ii)
      ], 8, Ci)) : Xe("", !0),
      u.value ? (J(), nn(M(d), { key: 1 })) : Xe("", !0)
    ], 64));
  }
});
function Ai(e) {
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
    return Promise.resolve(xi(e, t));
  }, i = (u = r.children) == null ? void 0 : u.map(
    (l) => Gn(l, t)
  ), s = {
    ...r,
    children: i,
    component: o
  };
  return r.component.length === 0 && delete s.component, i === void 0 && delete s.children, s;
}
function xi(e, t) {
  const { sid: n, vueItem: r } = e, { path: o, component: i } = r, s = ht(
    {
      items: i,
      sid: n
    },
    o
  ), u = A(rn, null, s);
  return t ? A(fr, null, () => s) : u;
}
function Ti(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? Ao() : n === "memory" ? $o() : Nn();
  e.use(
    Rs({
      history: r,
      routes: Ai(t)
    })
  );
}
function Wi(e, t) {
  e.component("insta-ui", wi), e.component("vif", Ln), e.component("vfor", Bn), e.component("match", Fn), e.component("teleport", Vi), e.component("icon", $i), e.component("ts-group", bi), e.component("content", Pi), e.component("heading", Ni), t.router && Ti(e, t);
}
export {
  Ae as convertDynamicProperties,
  Wi as install,
  Mi as useVarGetter
};
//# sourceMappingURL=insta-ui.js.map
