// import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    searchOptions: {
      // debounce: false, //关闭防抖
      valueChange: true // 搜索框开启valueChange
    },
    // selectionRow: {
    //   align: 'center',
    //   width: 30
    // },
    rowHandle: {
      dropdown: { // 操作列折叠
        atLeast: 3, // 至少几个以上的按钮才会被折叠,注意show=false的按钮也会计算在内（行编辑按钮默认是隐藏的也会占一个位置）
        text: '更多', // dropdown按钮文字
        type: 'primary'
      },
      width: 240,
      view: {
        show: false
      },
      edit: {
        show: false
      },
      remove: {
        show: false
      },
      custom: [
        {
          thin: true,
          text: '详情',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-view',
          show () {
            return vm.hasPermissions('serviceDetail')
          },
          emit: 'serviceDetail',
          order: 1
        },
        {
          thin: true,
          text: '修改',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-s-grid',
          show () {
            return vm.hasPermissions('serviceEdit')
          },
          emit: 'serviceEdit',
          order: 1
        },
        {
          thin: true,
          text: 'YAML',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-s-grid',
          show () {
            return vm.hasPermissions('serviceYaml')
          },
          emit: 'serviceYaml',
          order: 1
        },
        {
          thin: true,
          text: '删除',
          size: 'small',
          type: 'primary',
          icon: 'el-icon-s-grid',
          show () {
            return vm.hasPermissions('serviceDelete')
          },
          emit: 'serviceDelete',
          order: 1
        }
      ]
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 30
    },
    columns: [
      {
        title: '集群名称',
        key: 'k8s_cluster_name',
        sortable: true,
        width: 145,
        disabled: true,
        search: {
          disabled: false,
          props: {
            clearable: true
          }
        },
        type: 'select',
        dict: {
          url: '/api/container/cluster/',
          value: 'k8s_cluster_name'
        },
        form: {
          // show: true,
          valueChange (key, value, form, { getColumn, mode, component, immediate, getComponent }) {
            form.namespace = undefined // 将“namespace”的值置空
            if (value) {
              console.log('-----你选择了')
              vm.selectedClusterName = form.k8s_cluster_name
              console.log(vm.selectedClusterName)
              getComponent('namespace').reloadDict() // 执行namespace的select组件的reloadDict()方法，触发“namespace”重新加载字典
            }
          },
          valueChangeImmediate: false // 是否在编辑框打开后立即触发一次valueChange方法
        }
      },
      {
        title: '命名空间',
        key: 'namespace',
        sortable: true,
        width: 80,
        disabled: true,
        search: {
          disabled: false
        },
        type: 'select',
        dict: {
          url (dict, { form, component }) {
            if (form.k8s_cluster_name != null) {
              console.log('form.k8s_cluster_name is ' + form.k8s_cluster_name)
              return '/api/container/namespace/?cluster_name=' + form.k8s_cluster_name
            } else {
              return '/api/container/namespace/'
            }
          },
          immediate: true,
          value: 'namespace'
        },
        form: {
          disabled: true,
          // show: true,
          component: { props: { dict: { cache: false } } },
          valueChange (key, value) {
            vm.selectedNamespace = value
            console.log(this.selectedNamespace)
            console.log('您选择了：', value)
          }
        }
      },
      {
        title: '名称',
        key: 'service_name',
        width: 120,
        search: {
          disabled: false
        },
        dict: {
          cache: true,
          data: vm.dictionary('service_name')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '类型',
        key: 'service_type',
        width: 60,
        dict: {
          cache: true,
          data: vm.dictionary('service_type')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'cluster_ip',
        key: 'service_cluster_ip',
        width: 80,
        dict: {
          cache: true,
          data: vm.dictionary('service_cluster_ip')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '所属集群',
        key: 'cluster_name',
        width: 80,
        disabled: true,
        search: {
          disabled: true
        },
        dict: {
          cache: true,
          data: vm.dictionary('cluster_name')
        },
        form: {
          show: true
        }
      },
      {
        title: '端口',
        key: 'service_port',
        width: 140,
        rowSlot: true,
        dict: {
          cache: true,
          data: vm.dictionary('service_port')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: '创建时间',
        key: 'service_creat_time',
        width: 100,
        dict: {
          cache: true,
          data: vm.dictionary('service_creat_time')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
