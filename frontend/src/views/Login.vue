<template>
    <form>
        Đăng nhập
        <legend>
            <label for="username">Username</label> <br>
            <input type="text" name="username"> <br>
            <label for="password">Password</label> <br>
            <input type="password" name="password"> <br>
            <button type="submit">Đăng nhập</button>
        </legend>
        <div @click="loginGG">Đăng nhập bằng Google</div>
        <div>Quên mật khẩu</div>
        <div>Đăng ký</div>
    </form>
</template>
<script setup>
import axios from 'axios';

async function loginGG() {
    const res = await axios.get("http://localhost:5000/api/oauth2/login_gg");
    const url = res.data;
    window.location.href = url;
}

</script>