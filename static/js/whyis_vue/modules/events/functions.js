/**
 * The functions below are used by the event services module
 * 1. "confirmAuth": Checks if user is authenticated
 * 2. "toggleNav"
 */


import { getViewUrl } from '../../utilities/views';
import { getCharts } from '../../utilities/vega-chart';

/** NEEDED FOR NANOMINE */
const LOCAL_DEV_SERVER = 'http://localhost:8000/nmr/chart';
const SERVER = `${ROOT_URL}nmr/chart`;
const URL = LOCAL_DEV_SERVER;

const controller = {
  confirmAuth(){
    if(Object.keys(USER).length){
      this.authUser = {...USER};
      this.authUser.email = 'testuser'
      this.$emit('snacks', {status: true});
      return this.$emit('isauthenticated', this.authUser);
    }
  },

  toggleNav() {
    this.navOpen = !this.navOpen;
    return this.$emit('togglenavigation', this.navOpen);
  },

  confirmConfig(){
    const { mongoBackup, speedDialIcon } = CONFIGS
    this.thirdPartyRestBackup = mongoBackup == "True" ? true : false;
    this.speedDials = speedDialIcon == "True" ? true : false;
  },

  navTo(args, uri){
    if(uri){
      return window.location = `${window.location.origin}/about?view=${args}&uri=http:%2F%2Fsemanticscience.org%2Fresource%2FChart`
      // return window.location = `${window.location.origin}/wi/about?view=${args}&uri=http:%2F%2Fsemanticscience.org%2Fresource%2FChart`
    }
    return window.location=args
  },

  checkIfRestValidate(){
    if(!this.authUser){
      const err = new Error('User Authorization Failed!')
      throw err;
    }
    if(!this.thirdPartyRestBackup) {
      return false
    }
    return true
  },

  async restCallFn(formData, URL, METHOD){
    const forms = formData ? {...formData} : undefined
    try {
      let result = await fetch(URL, {
        method: METHOD,
        headers: {
          Accept: '*/*',
          'Content-Type': 'application/json',
          // Authorization: 'Bearer' + cookies
        },
        body: JSON.stringify(forms)
      })
      if(result.status == 201) {
        result = await result.json()
        return result
      }
      return undefined
    } catch(err){
      throw err;
    }
  },

  async loadVisualization (args) {
    /** passing view=instances&uri=this.parsedArg */ 
    let data, processedData, uri;
    uri = NODE_URI
    const pageUri = getViewUrl(args, "instances")
    data = await fetch(pageUri, {
      method: "POST"
    });
    processedData = await data.json();
    return processedData;
  },

  async loadCharts(){
    let result;
    result = await getCharts()
    console.log('whyischartloader', result)
    if(result.length){
      result = result.map((el) => {
        el.backup = el
        return el
      })
      return this.chartListings = result
    }
  },

  async fetchAllCharts(){
    if(!this.thirdPartyRestBackup) {
      return this.loadCharts()
    }
    const existingBookmark = await JSON.parse(localStorage.getItem('chartbkmk'));
    let result = await this.restCallFn(undefined, `${URL}/retrievecharts`, 'GET');
    if(result) {
      result = result.charts.map((el) => {
        el.backup = JSON.parse(el.backup)
        return el
      })
      if(!this.filterExist){
        if(!existingBookmark){
          return this.chartListings = result;
        } else {
          const filter = await result.filter(function(o1){
            return existingBookmark.some(function(o2){
              if(o2 && o2.chart){
                return o1.name === o2.chart.name;          
              }
            });
          })
          await filter.forEach(el => {
            el.bookmark = true;
          })
          return this.chartListings = result;
        }
      }
    }
  },

  async createBackUp(args, prevID, enabled, tags){
    if(this.checkIfRestValidate()){
      const uri = args && args.uri ? args.uri.split("/"): null;
      const name = uri != null ? uri[uri.length - 1] : null;
      const prevChartID = !prevID ? 'null' : prevID;
      const eStatus = !enabled ? false : true;
      const restored = !prevID ? false : true;
      const formData = {name: name, chart: args, creator: this.authUser.email, prevChartID: prevChartID, tag:tags, enabled:eStatus, restored:restored}
      return this.restCallFn(formData, `${URL}/postcharts`, 'POST')
    }
  },

  async deleteAChart(chart) {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({name: chart._id, creator: this.authUser.email}, `${URL}/deletecharts`, 'DELETE')
      if(result){
        this.chartListings.find((el, index) => {
          if(el == chart){
            this.chartListings.splice(index, 1)
          }
        })
        return listNanopubs(chart.backup.uri)
          .then(nanopubs => nanopubs.map(nanopub => deleteNanopub(nanopub.np)))
          .then(() => {
            this.getState();
            return this.$emit('snacks', {status:true, message: "Chart Deleted Successfully!"})
          })
          .catch(err => {
            throw err
          })
      }
    }
  },

  async resetChart() {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({creator: this.authUser.email}, `${URL}/resetcharts`, 'POST')
      if(result){
        await this.fetchAllCharts();
        return this.$emit('snacks', {status:true, message: 'Chart Reset Completed'});
      }
      return this.$emit('snacks', {status:true, message: err, tip: "Try Again"});
    }
  },

  async getUserBkmk (){
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({creator: this.authUser.email}, `${URL}/retrievechartbkmks`, 'POST')
      if(result){
        if(result.charts.length > 0){
          localStorage.setItem('chartbkmk', JSON.stringify(result.charts));
        }
        return this.fetchAllCharts();
      }
      return this.$emit('snacks', {status:true, message: 'Error retreiving bookmarks', tip: "Refresh App"});
    }
  },

  async createChartBookMark(args, exist) {
    if(this.checkIfRestValidate()){
      const result = await this.restCallFn({bkmk:args, status:exist, creator: this.authUser.email}, `${URL}/postchartbkmks`, 'POST')
      if(result){
        localStorage.removeItem('chartbkmk');
        this.getUserBkmk()
        return this.$emit('savedbookmark', {status:true, message: exist ? "Bookmark Removed!": "Bookmark Saved!"});
      }
      return this.$emit('savedbookmark', {status:true, message: 'Bookmark Error!', tip: "Try Again"});
    }
  },

  async filterChart(key, args, user) {
    let filter = [];
    if(!user) {
      this.chartListings.map((el) => {
        if(el.backup[key] == args){
          filter.push(el)
        }
      })
    } else {
      this.chartListings.map((el) => {
        if(el[key] == usermail){
          filter.push(el)
        }
      })
    }
    this.filterExist = true;
    return this.$emit('filterexist', filter);
  },

  cancelChartFilter(){
    this.filterExist = false;
    return this.$emit('filterexistcancel', this.chartListings)
  },

  getState(){
    return this.$emit('appstate', this.chartListings);
  },

  async tipController(arg) {
    const checkIntroStatus = await JSON.parse(localStorage.getItem('introstatus'));
    if(arg){
      return this.$emit("dialoguebox", {status: true, intro: true})
    }

    if(!checkIntroStatus){
      localStorage.setItem('introstatus', JSON.stringify(true));
      return this.$emit("dialoguebox", {status: true, intro: true});
    }
  },

  checkIfEditable(args){
    if(this.checkIfRestValidate()){
      /** TODO: Filter chartlistings and check if user/admin */
      if(args){
        const uri = args.split("/");
        const name = uri[uri.length - 1] ;
        this.$emit("allowChartEdit", true)
      }
    }
  }
}



export {
  controller
}