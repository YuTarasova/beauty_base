<template>
  <div class="first-layer">
    <div class="second-layer">
      <span>Клиенты</span>
      <label class="switch">
        <input type="checkbox" v-model="mode" />
        <span class="slider"></span>
      </label>
      <span>Сотрудники</span>
      <div v-if="mode">
        <form id="st-login">
          <label
            >ID<span style="color: red">*</span><br />
            <input type="number" name="staff_id" min="0" max="65535" required />
          </label>
          <br />
          <label
            >Пароль<span style="color: red">*</span><br />
            <input
              type="password"
              name="password"
              pattern="^[\w@#%~\u0024\u005e]{6,32}$"
              required
              placeholder="Введите пароль"
            />
          </label>
          <br />
          <button type="button" @click="st_login">Войти</button>
        </form>
      </div>
      <div v-else>
        <span>Вход</span>
        <label class="switch">
          <input type="checkbox" v-model="reglog" />
          <span class="slider"></span>
        </label>
        <span>Регистрация</span>
        <div v-if="reglog">
          <form id="cl-reg">
            <label
              >Имя<span style="color: red">*</span><br />
              <input
                type="text"
                name="first_name"
                pattern="^[А-Я][-а-яА-Я\u0020]{0,31}$"
                required
                placeholder="Введите имя"
              />
            </label>
            <br />
            <label
              >Фамилия<br />
              <input
                type="text"
                name="last_name"
                pattern="^[А-Я][-а-яА-Я\u0020]{0,31}$"
                placeholder="Введите фамилию"
              />
            </label>
            <br />
            <label
              >Номер телефона<span style="color: red">*</span><br />
              <small
                >Формат: 00000000000<br />
                т.е. если ваш номер +1 (234) 567-89-01, введите
                12345678901</small
              ><br />
              <input
                type="number"
                name="phone"
                min="10000000000"
                max="99999999999"
                required
                placeholder="XXXXXXXXXXX"
              />
            </label>
            <br />
            <label
              >Пароль<span style="color: red">*</span><br />
              <small
                >Латинские буквы, цифры и символы '@', '#', '$', '%', '^', '~',
                '_'. Длиной от 6 до 32 символов.</small
              ><br />
              <input
                type="password"
                name="password"
                pattern="^[\w@#%~\u0024\u005e]{6,32}$"
                required
                placeholder="Введите пароль"
              />
            </label>
            <br />
            <button type="button" @click="cl_reg">Зарегистрироваться</button>
          </form>
        </div>
        <div v-else>
          <form id="cl-login">
            <label
              >Номер телефона<span style="color: red">*</span><br />
              <small>Формат: 00000000000</small><br />
              <input
                type="number"
                name="phone"
                min="10000000000"
                max="99999999999"
                required
                placeholder="XXXXXXXXXXX"
              />
            </label>
            <br />
            <label
              >Пароль<span style="color: red">*</span><br />
              <input
                type="password"
                name="password"
                pattern="^[\w@#%~\u0024\u005e]{6,32}$"
                required
                placeholder="Введите пароль"
              />
            </label>
            <br />
            <button type="button" @click="cl_login">Войти</button>
          </form>
        </div>
      </div>
      <div id="mypopover" popover>{{ msg }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LogIn",
  props: {
    defurl: {
      type: String,
      required: true,
    },
  },
  emits: ["auth"],
  data() {
    return {
      mode: false,
      reglog: false,
      msg: "",
    };
  },
  methods: {
    async st_login() {
      const form = document.getElementById("st-login");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        const response = await fetch(this.defurl + "stf/login", {
          method: "POST",
          body: fD,
        });
        const data = await response.json();
        if (response.ok) {
          let role = fD.get("staff_id");
          role =
            role <= 100
              ? "Acc"
              : role <= 400
              ? "Head"
              : role <= 1000
              ? "Adm"
              : "Stf";

          this.$emit("auth", data.token, role);
        } else {
          this.msg = data.detail;
          document.getElementById("mypopover").showPopover();
        }
      }
    },
    async cl_reg() {
      let form = document.getElementById("cl-reg");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        const response = await fetch(this.defurl + "cli/register", {
          method: "POST",
          body: fD,
        });
        const data = await response.json();
        this.msg = data.detail;
        if (response.ok) {
          form.reset();
        }
        document.getElementById("mypopover").showPopover();
      }
    },
    async cl_login() {
      const form = document.getElementById("cl-login");
      if (form.checkValidity()) {
        const fD = new FormData(form);
        const response = await fetch(this.defurl + "cli/login", {
          method: "POST",
          body: fD,
        });
        const data = await response.json();
        if (response.ok) {
          this.$emit("auth", data.token, "Cli");
        } else {
          this.msg = data.detail;
          document.getElementById("mypopover").showPopover();
        }
      }
    },
  },
};
</script>

<style scoped>
.first-layer {
  background-color: #2d3441;
}
.second-layer {
  background-color: #cbcbdb;
  color: #010101;
}
input:invalid {
  border-color: #ffaf7d;
  border-width: 2px;
  background-color: #ffd988;
  color: #3f2a0a;
}
</style>
