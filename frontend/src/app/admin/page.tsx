"use client";

import { FormEvent, useEffect, useState } from "react";
import { formatYen } from "@/lib/api";

type User = { id: number; email: string; name: string; phone: string; is_admin: boolean };
type Product = { id: number; sku: string; slug: string; name: string; price_yen: number; color: string };
type Inquiry = {
  id: number;
  name: string;
  email: string;
  status: string;
  total_yen: number;
  message: string;
  country: string;
};
type Contact = { id: number; name: string; email: string; product: string; message: string };

export default function AdminPage() {
  const [me, setMe] = useState<User | null>(null);
  const [tab, setTab] = useState<"products" | "users" | "inquiries" | "contacts">("products");
  const [products, setProducts] = useState<Product[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [error, setError] = useState("");

  async function refresh() {
    const meRes = await fetch("/api/auth/me", { credentials: "include" });
    if (!meRes.ok) {
      setMe(null);
      return;
    }
    const user = await meRes.json();
    if (!user.is_admin) {
      setError("Admin only");
      setMe(null);
      return;
    }
    setMe(user);
    const [p, u, i, c] = await Promise.all([
      fetch("/api/admin/products", { credentials: "include" }).then((r) => r.json()),
      fetch("/api/admin/users", { credentials: "include" }).then((r) => r.json()),
      fetch("/api/admin/inquiries", { credentials: "include" }).then((r) => r.json()),
      fetch("/api/admin/contacts", { credentials: "include" }).then((r) => r.json()),
    ]);
    setProducts(p);
    setUsers(u);
    setInquiries(i);
    setContacts(c);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function login(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
    });
    if (!res.ok) {
      setError("Invalid credentials");
      return;
    }
    setError("");
    refresh();
  }

  async function saveProduct(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const sku = String(fd.get("sku"));
    await fetch("/api/admin/products", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sku,
        slug: String(fd.get("slug") || sku.toLowerCase()),
        price_yen: Number(fd.get("price_yen") || 0),
        color: fd.get("color") || "",
        image: fd.get("image") || "/assets/img/usr/slider/slider_lineup.jpg",
        translations: [
          { locale: "en", name: fd.get("name"), description: fd.get("description") || "" },
          { locale: "zh-CN", name: fd.get("name"), description: fd.get("description") || "" },
          { locale: "zh-HK", name: fd.get("name"), description: fd.get("description") || "" },
        ],
      }),
    });
    refresh();
    e.currentTarget.reset();
  }

  async function addUser(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    await fetch("/api/admin/users", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: fd.get("email"),
        password: fd.get("password"),
        name: fd.get("name"),
        is_admin: fd.get("is_admin") === "on",
      }),
    });
    refresh();
    e.currentTarget.reset();
  }

  if (!me) {
    return (
      <div className="admin">
        <h1>Admin login</h1>
        <form className="form" onSubmit={login}>
          <label>
            Email
            <input name="email" type="email" defaultValue="admin@example.com" required />
          </label>
          <label>
            Password
            <input name="password" type="password" required />
          </label>
          {error ? <p className="alert error">{error}</p> : null}
          <button className="btn-primary" type="submit">
            Log in
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="admin">
      <h1>Airdog admin — {me.email}</h1>
      <nav>
        <button type="button" onClick={() => setTab("products")}>
          Products
        </button>
        <button type="button" onClick={() => setTab("users")}>
          Users
        </button>
        <button type="button" onClick={() => setTab("inquiries")}>
          Inquiries
        </button>
        <button type="button" onClick={() => setTab("contacts")}>
          Contacts
        </button>
        <a href="/en">Storefront</a>
      </nav>

      {tab === "products" && (
        <>
          <h2>Products</h2>
          <form className="form" onSubmit={saveProduct}>
            <input name="sku" placeholder="SKU" required />
            <input name="slug" placeholder="slug" />
            <input name="name" placeholder="Name" required />
            <input name="price_yen" type="number" placeholder="Price JPY" required />
            <input name="color" placeholder="Color" />
            <input name="image" placeholder="Image URL" />
            <textarea name="description" placeholder="Description" />
            <button className="btn-primary" type="submit">
              Create product
            </button>
          </form>
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Price</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>{p.sku}</td>
                  <td>{p.name}</td>
                  <td>{formatYen(p.price_yen)}</td>
                  <td>
                    <button
                      type="button"
                      onClick={async () => {
                        await fetch(`/api/admin/products/${p.id}`, { method: "DELETE", credentials: "include" });
                        refresh();
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {tab === "users" && (
        <>
          <h2>Users</h2>
          <form className="form" onSubmit={addUser}>
            <input name="email" type="email" placeholder="Email" required />
            <input name="name" placeholder="Name" />
            <input name="password" placeholder="Password" required />
            <label>
              <input name="is_admin" type="checkbox" /> Admin
            </label>
            <button className="btn-primary" type="submit">
              Create user
            </button>
          </form>
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Name</th>
                <th>Admin</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{u.name}</td>
                  <td>{u.is_admin ? "yes" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {tab === "inquiries" && (
        <>
          <h2>Inquiries</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Total</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {inquiries.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.name}</td>
                  <td>{row.email}</td>
                  <td>{formatYen(row.total_yen)}</td>
                  <td>
                    <select
                      defaultValue={row.status}
                      onChange={async (e) => {
                        await fetch(`/api/admin/inquiries/${row.id}`, {
                          method: "PATCH",
                          credentials: "include",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ status: e.target.value }),
                        });
                      }}
                    >
                      <option value="new">new</option>
                      <option value="processing">processing</option>
                      <option value="quoted">quoted</option>
                      <option value="closed">closed</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {tab === "contacts" && (
        <>
          <h2>Contact messages</h2>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Product</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.email}</td>
                  <td>{c.product}</td>
                  <td>{c.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
