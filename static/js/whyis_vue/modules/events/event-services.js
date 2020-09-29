import Vue from 'vue';
import * as Fn from './functions';

const EventServices = new Vue({
    data:{
        chartListings: [],
        authUser: undefined,
        navOpen: false,
        tempChart: undefined,
        thirdPartyRestBackup: false,
        speedDials: false,
        filterExist: false,
        currentPage: 1,
        settingsPage: 1,
        vizOfTheDay: true,
    },
    watch:{
        chartListings(newVal, oldVal){
            if(newVal != oldVal){
                this.getState();
            }
        },
        authUser(newVal){
            if(newVal){
                if(newVal.name){
                    this.getUserBkmk()
                }
                this.$emit('isauthenticated', this.authUser);
            }
        }
    },
    methods: {...Fn.controller},
    created(){
        return this.confirmConfig()
    }
})


/** Outside Navigation Click Handler */
document.addEventListener("click", () => {
    EventServices.$data.navOpen = false;
});

export default EventServices;