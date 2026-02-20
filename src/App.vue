<template>
  <component
    v-if="activeComp === 'LogIn'"
    :is="activeComp"
    :defurl="defurl"
    @auth="auth"
  ></component>
  <component
    v-else
    :is="activeComp"
    :defurl="defurl"
    :token="token"
    @ret="ret"
  ></component>
</template>

<script>
import LogIn from "./components/LogIn.vue";
import CliSide from "./components/CliSide.vue";
import StfSide from "./components/StfSide.vue";
import AdmSide from "./components/AdmSide.vue";
import HeadSide from "./components/HeadSide.vue";
import AccSide from "./components/AccSide.vue";
export default {
  name: "App",
  components: {
    LogIn,
    CliSide,
    StfSide,
    AdmSide,
    HeadSide,
    AccSide,
  },
  data() {
    return {
      defurl: "//localhost:8002/",
      activeComp: "LogIn",
      token: "",
    };
  },
  methods: {
    auth(token, role) {
      this.token = token;
      this.activeComp = role + "Side";
    },
    ret() {
      this.activeComp = "LogIn";
    },
  },
};
</script>
